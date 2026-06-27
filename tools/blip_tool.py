from pathlib import Path

from PIL import Image


class BlipTool:
    def __init__(self, device=None):
        self.torch = None
        self.device = device
        self.model_name = "Salesforce/blip-image-captioning-base"
        self.processor = None
        self.model = None
        self.fallback_caption = "An uploaded image"

    def _load_model(self):
        if self.processor is not None and self.model is not None:
            return

        print("[BLIP] Loading BLIP model...")
        import torch
        from transformers import BlipForConditionalGeneration, BlipProcessor

        self.torch = torch
        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = BlipProcessor.from_pretrained(self.model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(
            self.model_name
        ).to(self.device)
        self.model.eval()

    def generate_caption(self, image) -> str:
        print("[BLIP] Generating caption...")

        if image is None:
            return "No image provided"

        try:
            self._load_model()
            pil_image = self._to_rgb_image(image)
            inputs = self.processor(
                pil_image,
                return_tensors="pt",
            ).to(self.device)

            with self.torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=30,
                )

            caption = self.processor.decode(
                output[0],
                skip_special_tokens=True,
            ).strip()
            caption = caption or self.fallback_caption
            print(f"[BLIP] Caption: {caption}")
            return caption
        except Exception as error:
            print(f"[BLIP] Error: {error}")
            return self.fallback_caption

    def _to_rgb_image(self, image):
        if isinstance(image, Image.Image):
            return image.convert("RGB")

        if isinstance(image, (str, Path)):
            return Image.open(image).convert("RGB")

        if hasattr(image, "convert"):
            return image.convert("RGB")

        return Image.fromarray(image).convert("RGB")
