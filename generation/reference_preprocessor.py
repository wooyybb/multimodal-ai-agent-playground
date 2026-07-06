from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat


class ReferenceAnalyzer:
    def analyze(self, image: Image.Image) -> dict:
        image = image.convert("RGB")
        width, height = image.size
        background_ratio = self._background_ratio(image)
        character_ratio = max(0.0, min(1.0, 1.0 - background_ratio))
        face_ratio = self._estimated_face_ratio(width, height, character_ratio)
        quality = self._quality(width, height, character_ratio)
        return {
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 4) if height else 0.0,
            "character_ratio": round(character_ratio, 4),
            "background_ratio": round(background_ratio, 4),
            "face_ratio": round(face_ratio, 4),
            "estimated_focus": "center",
            "quality": quality,
        }

    def _background_ratio(self, image):
        small = image.resize((64, 64))
        border = Image.new("RGB", small.size, self._border_color(small))
        diff = ImageChops.difference(small, border).convert("L")
        threshold = diff.point(lambda value: 255 if value > 24 else 0)
        foreground = ImageStat.Stat(threshold).mean[0] / 255.0
        return 1.0 - foreground

    def _border_color(self, image):
        width, height = image.size
        pixels = []
        for x in range(width):
            pixels.append(image.getpixel((x, 0)))
            pixels.append(image.getpixel((x, height - 1)))
        for y in range(height):
            pixels.append(image.getpixel((0, y)))
            pixels.append(image.getpixel((width - 1, y)))
        channels = list(zip(*pixels))
        return tuple(int(sum(channel) / len(channel)) for channel in channels)

    def _estimated_face_ratio(self, width, height, character_ratio):
        if character_ratio <= 0:
            return 0.0
        image_area = max(1, width * height)
        estimated_face_area = image_area * character_ratio * 0.12
        return min(1.0, estimated_face_area / image_area)

    def _quality(self, width, height, character_ratio):
        shortest = min(width, height)
        if shortest >= 768 and 0.08 <= character_ratio <= 0.85:
            return "good"
        if shortest >= 512 and character_ratio > 0.03:
            return "medium"
        return "poor"


class ReferencePreprocessor:
    def __init__(self, output_dir="outputs"):
        self.output_dir = Path(output_dir)
        self.analyzer = ReferenceAnalyzer()

    def condition(
        self,
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> tuple[Image.Image, dict]:
        print("[ReferenceConditioning] Analyzing reference image...")
        original = image.convert("RGB")
        analysis = self.analyzer.analyze(original)
        print(f"[ReferenceConditioning] Reference Width: {analysis['width']}")
        print(f"[ReferenceConditioning] Reference Height: {analysis['height']}")
        print(f"[ReferenceConditioning] Character Ratio: {analysis['character_ratio']}")

        conditioned, steps = self._resize_crop_or_pad(
            original,
            target_width,
            target_height,
        )
        path = self._save(conditioned)
        summary = {
            "reference_analysis": analysis,
            "conditioning_summary": {
                "target_width": target_width,
                "target_height": target_height,
                "crop_applied": steps["crop_applied"],
                "padding_applied": steps["padding_applied"],
                "resize_applied": steps["resize_applied"],
                "aspect_ratio_preserved": True,
                "method": steps["method"],
            },
            "conditioned_reference_path": path,
            "conditioning_package": {
                "reference_image": "PIL.Image",
                "conditioned_reference": path,
                "conditioning_info": steps,
            },
        }
        print(f"[ReferenceConditioning] Crop Applied: {steps['crop_applied']}")
        print(f"[ReferenceConditioning] Padding Applied: {steps['padding_applied']}")
        print(f"[ReferenceConditioning] Resize Applied: {steps['resize_applied']}")
        return conditioned, summary

    def _resize_crop_or_pad(self, image, target_width, target_height):
        target_ratio = target_width / target_height
        source_width, source_height = image.size
        source_ratio = source_width / source_height if source_height else target_ratio
        steps = {
            "crop_applied": False,
            "padding_applied": False,
            "resize_applied": False,
            "method": "aspect_ratio_preserve",
        }

        ratio_delta = abs(source_ratio - target_ratio)
        if ratio_delta <= 0.08:
            conditioned = ImageOps.contain(image, (target_width, target_height))
            steps["resize_applied"] = conditioned.size != image.size
            conditioned = ImageOps.pad(
                conditioned,
                (target_width, target_height),
                method=Image.Resampling.LANCZOS,
                color=self._padding_color(conditioned),
                centering=(0.5, 0.5),
            )
            steps["padding_applied"] = conditioned.size != image.size
            steps["method"] = "longest_edge_resize_with_padding"
            return conditioned, steps

        if ratio_delta <= 0.35:
            conditioned = ImageOps.fit(
                image,
                (target_width, target_height),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            steps["crop_applied"] = True
            steps["resize_applied"] = True
            steps["method"] = "auto_center_crop"
            return conditioned, steps

        conditioned = ImageOps.contain(
            image,
            (target_width, target_height),
            method=Image.Resampling.LANCZOS,
        )
        conditioned = ImageOps.pad(
            conditioned,
            (target_width, target_height),
            method=Image.Resampling.LANCZOS,
            color=self._padding_color(conditioned),
            centering=(0.5, 0.5),
        )
        steps["padding_applied"] = True
        steps["resize_applied"] = True
        steps["method"] = "auto_padding"
        return conditioned, steps

    def _padding_color(self, image):
        stat = ImageStat.Stat(image.resize((1, 1)))
        return tuple(int(value) for value in stat.mean)

    def _save(self, image):
        self.output_dir.mkdir(exist_ok=True)
        path = self.output_dir / "conditioned_reference.png"
        image.save(path)
        return str(path)
