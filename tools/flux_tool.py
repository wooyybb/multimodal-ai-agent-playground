import os
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


class FluxTool:
    def __init__(self, output_dir="outputs", model_name=None):
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except Exception:
            pass

        self.output_dir = Path(output_dir)
        self.model_name = model_name or "black-forest-labs/FLUX.1-schnell"
        self.hf_token = os.getenv("HF_TOKEN")

    def generate(self, prompt: str) -> str:
        print("[FLUX] Running generation...")
        prompt = prompt.strip() if prompt else "high quality generated image"
        output_path = self._build_output_path()

        if self.hf_token:
            print("[FLUX] HF_TOKEN found. Trying real FLUX generation...")
            try:
                image = self._generate_with_flux(prompt)
                self._save_image(image, output_path)
                print(f"[FLUX] Real generation succeeded: {output_path}")
                return str(output_path)
            except Exception as error:
                print(
                    "[FLUX] Real generation failed. "
                    "Using fallback mock image."
                )
                print(f"[FLUX] Error: {error}")
        else:
            print("[FLUX] HF_TOKEN not found. Using fallback mock image.")

        image = self._create_fallback_image(prompt)
        self._save_image(image, output_path)
        return str(output_path)

    def _generate_with_flux(self, prompt):
        from huggingface_hub import InferenceClient

        client = InferenceClient(
            model=self.model_name,
            token=self.hf_token,
        )
        return client.text_to_image(prompt)

    def _create_fallback_image(self, prompt):
        image = Image.new("RGB", (768, 512), color=(245, 247, 250))
        draw = ImageDraw.Draw(image)

        draw.rectangle((32, 32, 736, 480), outline=(70, 90, 120), width=3)
        draw.text((56, 56), "Fallback FLUX Mock Output", fill=(30, 40, 60))
        draw.text((56, 96), "Prompt:", fill=(30, 40, 60))
        draw.text((56, 128), prompt[:160], fill=(70, 90, 120))
        return image

    def _build_output_path(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return self.output_dir / f"flux_output_{timestamp}.png"

    def _save_image(self, image, output_path):
        self.output_dir.mkdir(exist_ok=True)
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        image = image.convert("RGB")
        image.save(output_path)
