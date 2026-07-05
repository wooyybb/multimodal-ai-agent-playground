import os
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageDraw

from generation.generation_result import GenerationResult


class SDXLQualityProvider:
    name = "sdxl_quality"
    MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or self.MODEL_ID
        self.pipeline = None

    def generate(
        self,
        prompt: str,
        state: dict,
        fallback_generate=None,
        negative_prompt: str = "",
        config=None,
    ) -> GenerationResult:
        return self.run(prompt, negative_prompt, config, state=state)

    def run(
        self,
        prompt: str,
        negative_prompt: str = "",
        config=None,
        state: dict | None = None,
    ) -> GenerationResult:
        print("[GenerationRouter] Provider: sdxl_quality")
        started = perf_counter()
        state = state or {}
        config_dict = config.to_dict() if config else {}
        conditioning = self._conditioning_package(state)
        ip_adapter_status = self._ip_adapter_status(conditioning)
        notes = [
            "quality mode provider",
            "prompt-only generation",
            "IP Adapter hook planned",
            "ControlNet hook planned",
        ]
        notes.extend(conditioning.get("notes", []))
        used_fallback = False
        used_conditioning_fallback = bool(ip_adapter_status.get("used_fallback"))
        backend = "SDXL skeleton"

        try:
            if self._diffusers_enabled():
                output_path = self._generate_with_diffusers(
                    prompt,
                    negative_prompt,
                    config,
                    conditioning,
                    ip_adapter_status,
                )
                backend = "diffusers StableDiffusionXLPipeline"
            else:
                used_fallback = True
                notes.append("diffusers execution disabled; used mock fallback")
                output_path = self._create_mock_image(prompt, state, config)
        except Exception as error:
            used_fallback = True
            notes.append(f"SDXL diffusers unavailable: {error}")
            output_path = self._create_mock_image(prompt, state, config)

        return GenerationResult(
            output_image_path=output_path,
            generation_provider=self.name,
            generation_backend=backend,
            generation_mode="quality",
            generation_config=self._config_with_conditioning(config_dict, conditioning),
            latency=round(perf_counter() - started, 4),
            prompt_length=len(str(prompt or "").split()),
            generation_notes=notes,
            used_fallback=used_fallback,
            reference_conditioning_enabled=bool(conditioning.get("enabled")),
            conditioning_type=conditioning.get("conditioning_type", "none"),
            ip_adapter_enabled=bool(ip_adapter_status.get("enabled")),
            used_conditioning_fallback=used_conditioning_fallback,
            conditioning_reason=ip_adapter_status.get("reason", ""),
            ip_adapter_status=ip_adapter_status,
        )

    def _diffusers_enabled(self):
        return str(os.getenv("SDXL_ENABLE_DIFFUSERS") or "").lower() in {"1", "true", "yes"}

    def _generate_with_diffusers(self, prompt, negative_prompt, config, conditioning, ip_adapter_status):
        self._load_pipeline()
        self._apply_ip_adapter_hook(conditioning, ip_adapter_status)
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output_sdxl_quality.png"
        image = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            width=config.width,
            height=config.height,
            num_inference_steps=config.steps,
            guidance_scale=config.cfg,
        ).images[0]
        image.save(output_path)
        return str(output_path)

    def _apply_ip_adapter_hook(self, conditioning, ip_adapter_status):
        if not ip_adapter_status.get("should_attempt"):
            return
        try:
            model_path = ip_adapter_status.get("model_path")
            weight_name = ip_adapter_status.get("weight_name")
            if not model_path:
                raise ValueError("IP_ADAPTER_MODEL_PATH is not set")
            kwargs = {"weight_name": weight_name} if weight_name else {}
            self.pipeline.load_ip_adapter(model_path, **kwargs)
            if hasattr(self.pipeline, "set_ip_adapter_scale"):
                self.pipeline.set_ip_adapter_scale(conditioning.get("identity_strength", 0.75))
            ip_adapter_status["enabled"] = True
            ip_adapter_status["used_fallback"] = False
            ip_adapter_status["reason"] = "IP-Adapter hook loaded"
        except Exception as error:
            ip_adapter_status["enabled"] = False
            ip_adapter_status["used_fallback"] = True
            ip_adapter_status["reason"] = f"IP-Adapter fallback: {error}"

    def _load_pipeline(self):
        if self.pipeline is not None:
            return
        import torch
        from diffusers import StableDiffusionXLPipeline

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = self.pipeline.to(device)

    def _conditioning_package(self, state):
        package = state.get("reference_conditioning_package") or (
            state.get("compiled_prompt_package") or {}
        ).get("reference_conditioning_package") or {}
        normalized = {
            "enabled": bool(package.get("enabled")),
            "reference_image_path": package.get("reference_image_path", ""),
            "conditioning_type": package.get("conditioning_type", "none"),
            "identity_strength": package.get("identity_strength") or 0.75,
            "style_strength": package.get("style_strength") or 0.45,
            "structure_strength": package.get("structure_strength") or 0.40,
            "preserve": package.get("preserve", {}),
            "notes": list(package.get("notes") or []),
        }
        if normalized["enabled"] and normalized["conditioning_type"] == "ip_adapter_planned":
            normalized["notes"].append("IP-Adapter optional hook available in SDXL provider")
        return normalized

    def _ip_adapter_status(self, conditioning):
        use_ip_adapter = str(os.getenv("USE_IP_ADAPTER") or "false").lower() in {
            "1",
            "true",
            "yes",
        }
        status = {
            "enabled": False,
            "requested": use_ip_adapter,
            "model_path": os.getenv("IP_ADAPTER_MODEL_PATH", ""),
            "weight_name": os.getenv("IP_ADAPTER_WEIGHT_NAME", ""),
            "used_fallback": False,
            "reason": "IP-Adapter disabled",
            "should_attempt": False,
        }
        if not conditioning.get("enabled"):
            status["reason"] = "reference conditioning disabled"
            return status
        if not use_ip_adapter:
            status["reason"] = "IP-Adapter disabled"
            return status
        if not status["model_path"]:
            status["used_fallback"] = True
            status["reason"] = "IP_ADAPTER_MODEL_PATH is not set"
            return status
        if not Path(status["model_path"]).exists():
            status["used_fallback"] = True
            status["reason"] = "IP_ADAPTER_MODEL_PATH does not exist"
            return status
        status["should_attempt"] = True
        status["reason"] = "IP-Adapter hook pending pipeline load"
        return status

    def _config_with_conditioning(self, config_dict, conditioning):
        config = dict(config_dict or {})
        config["reference_conditioning"] = {
            "enabled": conditioning.get("enabled", False),
            "conditioning_type": conditioning.get("conditioning_type", "none"),
            "identity_strength": conditioning.get("identity_strength", 0.75),
            "style_strength": conditioning.get("style_strength", 0.45),
            "structure_strength": conditioning.get("structure_strength", 0.40),
            "preserve": conditioning.get("preserve", {}),
        }
        return config

    def _create_mock_image(self, prompt, state, config=None):
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output_sdxl_quality_mock.png"
        width = getattr(config, "width", None) or 1024
        height = getattr(config, "height", None) or 1024
        image = Image.new("RGB", (width, height), color=(235, 238, 242))
        draw = ImageDraw.Draw(image)
        lines = [
            "SDXL Quality Mode",
            f"CFG: {getattr(config, 'cfg', None)}",
            f"Steps: {getattr(config, 'steps', None)}",
            f"Scheduler: {getattr(config, 'scheduler', None)}",
            self._short(prompt),
        ]
        y = 32
        for line in lines:
            draw.text((32, y), line, fill=(24, 31, 42))
            y += 32
        image.save(output_path)
        return str(output_path)

    def _short(self, prompt, max_chars=90):
        value = str(prompt or "").replace("\n", " ").strip()
        if len(value) <= max_chars:
            return value
        return value[:max_chars].rstrip() + "..."
