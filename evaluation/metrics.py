from pathlib import Path

from PIL import Image

from tools.clip_tool import ClipTool


class BaseMetric:
    name = "base"

    def evaluate(self, state: dict) -> dict:
        raise NotImplementedError

    def _result(self, score, reason, enabled=True, used_fallback=False):
        return {
            "name": self.name,
            "score": self._clamp(score),
            "enabled": bool(enabled),
            "reason": reason,
            "used_fallback": bool(used_fallback),
        }

    def _clamp(self, score):
        try:
            value = float(score)
        except (TypeError, ValueError):
            value = 0.0
        return max(0.0, min(1.0, value))


class ClipMetric(BaseMetric):
    name = "clip"

    def __init__(self, clip_tool=None):
        self.clip_tool = clip_tool or ClipTool()

    def evaluate(self, state: dict) -> dict:
        prompt, prompt_type = self._select_prompt(state)
        print(f"[CLIPMetric] Using prompt type: {prompt_type}")
        try:
            score = self.clip_tool.evaluate(
                state.get("reference_image"),
                state.get("generated_image_path"),
                prompt,
            )
            result = self._result(score, "CLIP image-text similarity")
        except Exception as error:
            result = self._result(
                0.0,
                f"CLIP metric unavailable: {error}",
                enabled=False,
                used_fallback=True,
            )
        result["prompt_type"] = prompt_type
        result["prompt"] = prompt
        return result

    def _select_prompt(self, state):
        for key in ("clip_prompt", "evaluation_prompt", "provider_prompt", "user_prompt"):
            prompt = state.get(key)
            if prompt:
                return str(prompt), key
        return "", "empty"


class IdentityMetric(BaseMetric):
    name = "identity"

    def evaluate(self, state: dict) -> dict:
        prompt = str(
            state.get("generation_prompt")
            or state.get("provider_prompt")
            or state.get("final_prompt")
            or ""
        ).lower()
        character_program = state.get("character_program") or {}
        identity_terms = ("identity", "preserve", "recognizable", "character", "subject")
        accessory_terms = self._accessory_terms(character_program)

        score = 0.45
        if any(term in prompt for term in identity_terms):
            score += 0.25
        if character_program:
            score += 0.15
        if accessory_terms and any(term in prompt for term in accessory_terms):
            score += 0.15

        reason = "rule-based identity preservation check"
        if not character_program:
            reason += "; character_program unavailable"
        return self._result(score, reason)

    def _accessory_terms(self, character_program):
        appearance = character_program.get("appearance") or {}
        return [str(item).lower() for item in appearance.get("accessories", [])]


class PromptMetric(BaseMetric):
    name = "prompt"
    REQUIRED_HINTS = ("subject", "style", "layout", "lighting")

    def evaluate(self, state: dict) -> dict:
        package = state.get("compiled_prompt_package") or {}
        blocks = package.get("prompt_blocks") or {}
        context_program = state.get("context_program") or {}
        prompt = str(
            state.get("generation_prompt")
            or package.get("positive_prompt")
            or state.get("provider_prompt")
            or state.get("final_prompt")
            or state.get("user_prompt")
            or ""
        ).lower()
        negative_prompt = str(
            state.get("provider_negative_prompt")
            or state.get("negative_prompt")
            or (package.get("negative_prompt") if isinstance(package, dict) else "")
            or ""
        )

        if blocks:
            present = [key for key in self.REQUIRED_HINTS if blocks.get(key)]
            context_checks = self._context_checks(prompt, context_program)
            negative_separated = bool(negative_prompt)
            score = (
                len(present) / len(self.REQUIRED_HINTS) * 0.55
                + sum(context_checks.values()) / len(context_checks) * 0.35
                + (0.10 if negative_separated else 0.0)
            )
            reason = (
                f"prompt blocks present: {present}; "
                f"context checks: {context_checks}; "
                f"negative separated: {negative_separated}"
            )
        else:
            words = prompt.split()
            score = 0.75 if 8 <= len(words) <= 120 else 0.55
            reason = "prompt block data unavailable; used prompt length heuristic"

        result = self._result(score, reason)
        result["prompt_type"] = "generation_prompt"
        return result

    def _context_checks(self, prompt, context_program):
        characters = context_program.get("characters") or {}
        style = context_program.get("style") or {}
        layout = context_program.get("layout") or {}
        lighting = context_program.get("lighting") or {}
        return {
            "character": self._section_present(
                prompt,
                characters,
                ("character", "subject", "identity"),
            ),
            "style": self._section_present(
                prompt,
                style,
                ("style", "anime", "rendering"),
            ),
            "layout": self._section_present(
                prompt,
                layout,
                ("layout", "composition", "camera", "portrait"),
            ),
            "lighting": self._section_present(
                prompt,
                lighting,
                ("lighting", "light", "shadow", "mood"),
            ),
        }

    def _section_present(self, prompt, section, fallback_terms):
        if not section:
            return False
        section_text = self._flatten(section).lower()
        if any(term in prompt for term in fallback_terms):
            return True
        return any(token and token in prompt for token in section_text.split()[:12])

    def _flatten(self, value):
        if isinstance(value, dict):
            return " ".join(self._flatten(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._flatten(item) for item in value)
        return str(value or "")


class AestheticMetric(BaseMetric):
    name = "aesthetic"

    def evaluate(self, state: dict) -> dict:
        prompt = str(
            state.get("pickscore_prompt")
            or state.get("generation_prompt")
            or state.get("provider_prompt")
            or state.get("final_prompt")
            or state.get("user_prompt")
            or ""
        )
        negative = str(state.get("provider_negative_prompt") or state.get("negative_prompt") or "")
        words = prompt.split()

        score = 0.55
        if 12 <= len(words) <= 110:
            score += 0.2
        if any(
            term in prompt.lower()
            for term in ("high quality", "detailed", "lighting", "composition")
        ):
            score += 0.15
        if negative:
            score += 0.1

        result = self._result(score, "rule-based aesthetic prompt structure check")
        result["prompt_type"] = (
            "pickscore_prompt" if state.get("pickscore_prompt") else "generation_prompt"
        )
        return result


class DINOIdentityMetric(BaseMetric):
    name = "dino_identity"
    MODEL_NAME = "facebook/dinov2-small"

    def __init__(self, model_name=None, device=None):
        self.model_name = model_name or self.MODEL_NAME
        self.device = device
        self.processor = None
        self.model = None
        self.torch = None
        self.functional = None

    def evaluate(self, state: dict) -> dict:
        print("[DINOIdentityMetric] Running...")
        reference_image = self._reference_image(state)
        generated_image = self._generated_image(state)
        if not reference_image or not generated_image:
            return self._disabled("reference or generated image not available")

        try:
            self._load_model()
            reference_features = self._features(reference_image)
            generated_features = self._features(generated_image)
            similarity = self.functional.cosine_similarity(
                reference_features,
                generated_features,
            ).item()
            score = max(0.0, min(1.0, float((similarity + 1.0) / 2.0)))
            result = self._result(score, "DINOv2 image-image identity similarity")
            result["enabled"] = True
            result["used_fallback"] = False
            result["model"] = self.model_name
            self._log(result)
            return result
        except Exception as error:
            return self._disabled(f"DINO metric unavailable: {error}")

    def _reference_image(self, state):
        for key in ("reference_image_path", "image"):
            image = state.get(key)
            if self._is_image_like(image):
                return image
        reference = state.get("reference_image")
        if self._is_image_like(reference):
            return reference
        if isinstance(reference, dict):
            for key in ("image", "image_path", "path", "reference_image_path"):
                image = reference.get(key)
                if self._is_image_like(image):
                    return image
        return None

    def _generated_image(self, state):
        for key in (
            "generated_image_path",
            "best_output_image_path",
            "output_image_path",
            "retry_output_image_path",
        ):
            image = state.get(key)
            if self._is_image_like(image):
                return image
        return None

    def _is_image_like(self, image):
        if isinstance(image, Image.Image):
            return True
        if isinstance(image, (str, Path)):
            return Path(str(image)).exists()
        return hasattr(image, "convert")

    def _load_model(self):
        if self.processor is not None and self.model is not None:
            return
        import torch
        import torch.nn.functional as F
        from transformers import AutoImageProcessor, AutoModel

        self.torch = torch
        self.functional = F
        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def _features(self, image):
        image = self._to_rgb(image)
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with self.torch.no_grad():
            output = self.model(**inputs)
        features = getattr(output, "pooler_output", None)
        if features is None:
            features = output.last_hidden_state.mean(dim=1)
        return self.functional.normalize(features, p=2, dim=-1)

    def _to_rgb(self, image):
        if isinstance(image, Image.Image):
            return image.convert("RGB")
        if isinstance(image, (str, Path)):
            return Image.open(str(image)).convert("RGB")
        if hasattr(image, "convert"):
            return image.convert("RGB")
        raise ValueError("unsupported image input")

    def _disabled(self, reason):
        result = {
            "name": self.name,
            "score": 0.0,
            "enabled": False,
            "reason": reason,
            "used_fallback": True,
        }
        self._log(result)
        return result

    def _log(self, result):
        print(f"[DINOIdentityMetric] Enabled: {result.get('enabled')}")
        print(f"[DINOIdentityMetric] Score: {result.get('score')}")
        print(f"[DINOIdentityMetric] Reason: {result.get('reason')}")


CLIPMetric = ClipMetric

__all__ = [
    "AestheticMetric",
    "BaseMetric",
    "CLIPMetric",
    "ClipMetric",
    "DINOIdentityMetric",
    "IdentityMetric",
    "PromptMetric",
]
