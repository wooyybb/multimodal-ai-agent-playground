from tools.vlm.base_vlm import BaseVLM
from tools.vlm.blip_vlm import BLIPVLM
from pathlib import Path
from time import perf_counter

from PIL import Image


class FlorenceVLM(BaseVLM):
    MODEL_ID = "microsoft/Florence-2-base"
    CAPTION_TASK = "<CAPTION>"
    DETAILED_CAPTION_TASK = "<DETAILED_CAPTION>"
    OD_TASK = "<OD>"

    def __init__(self, blip_tool=None, model_id: str | None = None):
        self.fallback = BLIPVLM(
            blip_tool=blip_tool,
            provider="florence",
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
            caption = self._text_from_task_result(
                self._run_task(image_obj, self.CAPTION_TASK)
            )
            detailed_caption = self._text_from_task_result(
                self._run_task(image_obj, self.DETAILED_CAPTION_TASK)
            )
            od_result = self._run_task(image_obj, self.OD_TASK)
            objects = self._objects_from_od(od_result)
            object_names = [item["name"] for item in objects if item.get("name")]
            text = " ".join(
                [caption, detailed_caption, " ".join(object_names), prompt or ""]
            ).lower()
            fallback_parser = self.fallback
            character_hints = fallback_parser._character_hints(text)
            style_hints = fallback_parser._style_hints(text)
            composition_hints = fallback_parser._composition_hints(text)
            color_hints = fallback_parser._color_hints(text)
            if not objects:
                objects = self._objects_from_names(fallback_parser._objects(text))
            print(f"[FlorenceVLM] Caption task: {bool(caption)}")
            print(f"[FlorenceVLM] Detailed caption task: {bool(detailed_caption)}")
            print(f"[FlorenceVLM] Object detection count: {len(objects)}")
            return self.standard_result(
                caption=caption,
                detailed_caption=detailed_caption,
                objects=objects,
                regions=[],
                ocr=[],
                character_hints=character_hints,
                style_hints=style_hints,
                composition_hints=composition_hints,
                color_hints=color_hints,
                scene={
                    "summary": detailed_caption or caption,
                    "objects": objects,
                    "task_router": [
                        self.CAPTION_TASK,
                        self.DETAILED_CAPTION_TASK,
                        self.OD_TASK,
                    ],
                },
                style={"keywords": style_hints, "rendering": ", ".join(style_hints)},
                colors=color_hints,
                composition=composition_hints,
                model=self.model_id,
                provider="florence",
                used_fallback=False,
                latency=round(perf_counter() - started, 4),
            )
        except Exception as error:
            print(f"[FlorenceVLM] Fallback to BLIP: {error}")
            result = self.fallback.analyze(image, prompt=prompt)
            result["provider"] = "florence"
            result["model"] = "blip_fallback_for_florence"
            result["used_fallback"] = True
            result["latency"] = round(perf_counter() - started, 4)
            result["objects"] = self._objects_from_names(result.get("objects", []))
            result.setdefault("regions", [])
            result.setdefault("ocr", [])
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

    def _run_task(self, image, task_prompt):
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
        return parsed.get(task_prompt, parsed)

    def _text_from_task_result(self, value):
        if isinstance(value, dict):
            return " ".join(self._text_from_task_result(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._text_from_task_result(item) for item in value)
        return str(value)

    def _objects_from_od(self, value):
        data = value.get(self.OD_TASK, value) if isinstance(value, dict) else value
        if isinstance(data, dict):
            labels = data.get("labels") or data.get("label") or data.get("objects") or []
            bboxes = data.get("bboxes") or data.get("boxes") or data.get("bbox") or []
            if isinstance(labels, str):
                labels = [labels]
            objects = []
            for index, label in enumerate(labels):
                bbox = bboxes[index] if isinstance(bboxes, list) and index < len(bboxes) else []
                objects.append(self._object_dict(label, bbox))
            return [item for item in objects if item["name"]]
        if isinstance(data, list):
            objects = []
            for item in data:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("label") or item.get("class") or ""
                    bbox = item.get("bbox") or item.get("box") or item.get("bboxes") or []
                    objects.append(self._object_dict(name, bbox))
                else:
                    objects.append(self._object_dict(item, []))
            return [item for item in objects if item["name"]]
        return []

    def _objects_from_names(self, names):
        objects = []
        for item in names or []:
            if isinstance(item, dict):
                objects.append(
                    self._object_dict(
                        item.get("name") or item.get("label") or "",
                        item.get("bbox") or item.get("box") or [],
                    )
                )
            else:
                objects.append(self._object_dict(item, []))
        return [item for item in objects if item["name"]]

    def _object_dict(self, name, bbox):
        return {
            "name": str(name or "").strip(),
            "bbox": self._bbox_list(bbox),
        }

    def _bbox_list(self, bbox):
        if not isinstance(bbox, (list, tuple)):
            return []
        return [float(value) if isinstance(value, (int, float)) else value for value in bbox]
