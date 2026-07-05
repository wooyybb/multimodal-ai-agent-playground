from pathlib import Path

from PIL import Image

from evaluation.metric_base import BaseMetric


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
