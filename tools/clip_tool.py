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

            import torch
            import torch.nn.functional as F

            image = Image.open(generated_image_path).convert("RGB")

            inputs = self.processor(
                text=[final_prompt],
                images=image,
                return_tensors="pt",
                padding=True,
            )
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

                image_features = outputs.image_embeds
                text_features = outputs.text_embeds

                image_features = F.normalize(image_features, p=2, dim=-1)
                text_features = F.normalize(text_features, p=2, dim=-1)

                cosine = torch.sum(image_features * text_features, dim=-1).item()

            score = (cosine + 1.0) / 2.0
            score = max(0.0, min(1.0, float(score)))

            print(f"[CLIP] Score: {score:.4f}")
            return score

        except Exception as e:
            print("[CLIP] Error:", e)
            return 0.0