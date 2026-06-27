from pathlib import Path

from PIL import Image, ImageDraw


class FluxTool:
    def generate(self, prompt: str) -> str:
        print("[FLUX] Generating mock image...")

        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output_mock.png"

        image = Image.new("RGB", (768, 512), color=(245, 247, 250))
        draw = ImageDraw.Draw(image)

        draw.rectangle((32, 32, 736, 480), outline=(70, 90, 120), width=3)
        draw.text((56, 56), "Mock FLUX Output", fill=(30, 40, 60))
        draw.text((56, 96), "Prompt:", fill=(30, 40, 60))
        draw.text((56, 128), prompt[:160], fill=(70, 90, 120))

        image.save(output_path)
        return str(output_path)
