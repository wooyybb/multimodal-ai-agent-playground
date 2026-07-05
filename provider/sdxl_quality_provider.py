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
        notes = [
            "quality mode provider",
            "prompt-only generation",
            "IP Adapter hook planned",
            "ControlNet hook planned",
        ]
        used_fallback = False
        backend = "SDXL skeleton"

        try:
            if self._diffusers_enabled():
                output_path = self._generate_with_diffusers(prompt, negative_prompt, config)
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
            generation_config=config_dict,
            latency=round(perf_counter() - started, 4),
            prompt_length=len(str(prompt or "").split()),
            generation_notes=notes,
            used_fallback=used_fallback,
        )

    def _diffusers_enabled(self):
        return str(os.getenv("SDXL_ENABLE_DIFFUSERS") or "").lower() in {"1", "true", "yes"}

    def _generate_with_diffusers(self, prompt, negative_prompt, config):
        self._load_pipeline()
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
