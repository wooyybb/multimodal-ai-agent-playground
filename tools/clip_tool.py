from pathlib import Path

from PIL import Image


class ClipTool:
    def __init__(self, device=None):
        self.torch = None
        self.device = device
        self.model_name = "openai/clip-vit-base-patch32"
        self.processor = None
        self.model = None
        self.fallback_score = 0.0

    def _load_model(self):
        if self.processor is not None and self.model is not None:
            return

        print("[CLIP] Loading CLIP model...")
        import torch
        from transformers import CLIPModel, CLIPProcessor

        self.torch = torch
        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = CLIPProcessor.from_pretrained(self.model_name)
        self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def evaluate(self, reference_image, generated_image_path, final_prompt) -> float:
        print("[CLIP] Evaluating image-text similarity...")

        if not generated_image_path or not Path(generated_image_path).exists():
            return self.fallback_score

        if not final_prompt or not final_prompt.strip():
            return self.fallback_score

        try:
            self._load_model()
            image = Image.open(generated_image_path).convert("RGB")
            inputs = self.processor(
                text=[final_prompt],
                images=image,
                return_tensors="pt",
                padding=True,
            ).to(self.device)

            with self.torch.no_grad():
                image_features = self.model.get_image_features(
                    pixel_values=inputs["pixel_values"]
                )
                text_features = self.model.get_text_features(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                )

                cosine_similarity = self.torch.nn.functional.cosine_similarity(
                    image_features,
                    text_features,
                ).item()

            score = (cosine_similarity + 1) / 2
            score = round(max(0.0, min(score, 1.0)), 3)
            print(f"[CLIP] Score: {score}")
            return score
        except Exception as error:
            print(f"[CLIP] Error: {error}")
            return self.fallback_score
