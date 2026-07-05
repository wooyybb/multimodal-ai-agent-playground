from pathlib import Path

from PIL import Image, ImageDraw


class SDXLQualityProvider:
    name = "sdxl_quality"

    def generate(self, prompt: str, state: dict, fallback_generate=None) -> dict:
        print("[GenerationRouter] Provider: sdxl_quality")
        print("[SDXLQualityProvider] Skeleton provider active. No real SDXL call.")
        output_path = self._create_mock_image(prompt, state)
        return {
            "output_image_path": output_path,
            "generation_provider": self.name,
            "generation_backend": "SDXL skeleton",
            "generation_mode": "quality",
            "generation_notes": [
                "quality mode skeleton",
                "real SDXL model call not implemented",
                "IP Adapter hook planned",
                "ControlNet hook planned",
            ],
        }

    def _create_mock_image(self, prompt, state):
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output_sdxl_quality_mock.png"
        resolution = str((state.get("generation_plan") or {}).get("resolution") or "1024x1024")
        width, height = self._resolution(resolution)
        image = Image.new("RGB", (width, height), color=(235, 238, 242))
        draw = ImageDraw.Draw(image)
        lines = [
            "SDXL Quality Mode",
            f"CFG: {(state.get('generation_plan') or {}).get('cfg')}",
            f"Steps: {(state.get('generation_plan') or {}).get('steps')}",
            f"Scheduler: {(state.get('generation_plan') or {}).get('scheduler')}",
            self._short(prompt),
        ]
        y = 32
        for line in lines:
            draw.text((32, y), line, fill=(24, 31, 42))
            y += 32
        image.save(output_path)
        return str(output_path)

    def _resolution(self, value):
        try:
            width, height = str(value).lower().split("x", 1)
            return max(256, int(width)), max(256, int(height))
        except (TypeError, ValueError):
            return 1024, 1024

    def _short(self, prompt, max_chars=90):
        value = str(prompt or "").replace("\n", " ").strip()
        if len(value) <= max_chars:
            return value
        return value[:max_chars].rstrip() + "..."
