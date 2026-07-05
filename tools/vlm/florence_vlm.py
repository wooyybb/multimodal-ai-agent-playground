from tools.vlm.base_vlm import BaseVLM
from tools.vlm.blip_vlm import BLIPVLM
from pathlib import Path
from time import perf_counter

from PIL import Image


class FlorenceVLM(BaseVLM):
    MODEL_ID = "microsoft/Florence-2-base"

    def __init__(self, blip_tool=None, model_id: str | None = None):
        self.fallback = BLIPVLM(
            blip_tool=blip_tool,
            provider="florence2",
            model="blip_fallback_for_florence",
            used_fallback=True,
        )
        self.model_id = model_id or self.MODEL_ID
        self.processor = None
        self.model = None

    def analyze(self, image, prompt: str | None = None) -> dict:
        print("[FlorenceVLM] Analyzing image with Florence-2...")
        started = perf_counter()
        try:
            self._ensure_model()
            image_obj = self._load_image(image)
            caption = self._generate(image_obj, "<CAPTION>")
            detailed_caption = self._generate(image_obj, "<MORE_DETAILED_CAPTION>")
            text = " ".join([caption, detailed_caption, prompt or ""]).lower()
            fallback_parser = self.fallback
            character_hints = fallback_parser._character_hints(text)
            style_hints = fallback_parser._style_hints(text)
            composition_hints = fallback_parser._composition_hints(text)
            color_hints = fallback_parser._color_hints(text)
            objects = fallback_parser._objects(text)
            return self.standard_result(
                caption=caption,
                detailed_caption=detailed_caption,
                objects=objects,
                character_hints=character_hints,
                style_hints=style_hints,
                composition_hints=composition_hints,
                color_hints=color_hints,
                scene={"summary": detailed_caption or caption, "objects": objects},
                style={"keywords": style_hints, "rendering": ", ".join(style_hints)},
                colors=color_hints,
                composition=composition_hints,
                model=self.model_id,
                provider="florence2",
                used_fallback=False,
                latency=round(perf_counter() - started, 4),
            )
        except Exception as error:
            print(f"[FlorenceVLM] Fallback to BLIP: {error}")
            result = self.fallback.analyze(image, prompt=prompt)
            result["provider"] = "florence2"
            result["model"] = "blip_fallback_for_florence"
            result["used_fallback"] = True
            result["latency"] = round(perf_counter() - started, 4)
            return result

    def _ensure_model(self):
        if self.processor is not None and self.model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoProcessor

        self.processor = AutoProcessor.from_pretrained(
            self.model_id,
            trust_remote_code=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            trust_remote_code=True,
        )

    def _load_image(self, image):
        if isinstance(image, Image.Image):
            return image.convert("RGB")
        if image and Path(str(image)).exists():
            return Image.open(str(image)).convert("RGB")
        raise ValueError("Florence-2 requires a valid image path or PIL image.")

    def _generate(self, image, task_prompt):
        inputs = self.processor(
            text=task_prompt,
            images=image,
            return_tensors="pt",
        )
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=128,
            num_beams=3,
        )
        generated_text = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=False,
        )[0]
        parsed = self.processor.post_process_generation(
            generated_text,
            task=task_prompt,
            image_size=(image.width, image.height),
        )
        value = parsed.get(task_prompt, parsed)
        if isinstance(value, dict):
            return " ".join(str(item) for item in value.values())
        return str(value)
