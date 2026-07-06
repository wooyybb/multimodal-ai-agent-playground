import os
from pathlib import Path

from PIL import Image, ImageFilter


class ControlNetHook:
    SUPPORTED = {"openpose", "depth", "canny"}

    def prepare(self, reference_image: Image.Image | None, output_dir="outputs") -> dict:
        enabled = str(os.getenv("USE_CONTROLNET") or "false").lower() in {
            "1",
            "true",
            "yes",
        }
        control_type = str(os.getenv("CONTROLNET_TYPE") or "canny").lower()
        scale = self._scale()
        status = {
            "enabled": enabled,
            "loaded": False,
            "type": control_type,
            "scale": scale,
            "model_id": os.getenv("CONTROLNET_MODEL_ID", ""),
            "control_image_path": "",
            "used_fallback": False,
            "fallback_reason": "",
            "reason": "ControlNet disabled" if not enabled else "ControlNet pending",
        }
        if not enabled:
            self._log(status)
            return status
        if control_type not in self.SUPPORTED:
            status["used_fallback"] = True
            status["fallback_reason"] = f"unsupported ControlNet type: {control_type}"
            status["reason"] = status["fallback_reason"]
            self._log(status)
            return status

        if reference_image is None:
            status["used_fallback"] = True
            status["fallback_reason"] = "reference image unavailable for ControlNet"
            status["reason"] = status["fallback_reason"]
            self._log(status)
            return status

        if control_type != "canny":
            status["used_fallback"] = True
            status["fallback_reason"] = (
                f"ControlNet {control_type} hook planned; only canny is implemented"
            )
            status["reason"] = status["fallback_reason"]
            self._log(status)
            return status

        try:
            status["control_image_path"] = self._create_canny_image(
                reference_image,
                output_dir,
            )
            status["reason"] = "Canny control image generated"
        except Exception as error:
            status["used_fallback"] = True
            status["fallback_reason"] = f"canny control image failed: {error or repr(error)}"
            status["reason"] = status["fallback_reason"]
        self._log(status)
        return status

    def mark_loaded(self, status):
        status = dict(status or {})
        status["loaded"] = True
        status["reason"] = "ControlNet pipeline loaded"
        self._log(status)
        return status

    def mark_fallback(self, status, reason):
        status = dict(status or {})
        status["loaded"] = False
        status["used_fallback"] = True
        status["fallback_reason"] = reason
        status["reason"] = reason
        self._log(status)
        return status

    def _create_canny_image(self, image, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "control_canny.png"
        gray = image.convert("L")
        try:
            import cv2
            import numpy as np

            array = np.array(gray)
            edges = cv2.Canny(array, 100, 200)
            control = Image.fromarray(edges).convert("RGB")
        except Exception:
            control = gray.filter(ImageFilter.FIND_EDGES).convert("RGB")
        control.save(output_path)
        return str(output_path)

    def _scale(self):
        try:
            return float(os.getenv("CONTROLNET_SCALE") or 0.6)
        except (TypeError, ValueError):
            return 0.6

    def _log(self, status):
        print(f"[ControlNet] Enabled: {status.get('enabled')}")
        print(f"[ControlNet] Type: {status.get('type')}")
        print(f"[ControlNet] Scale: {status.get('scale')}")
        print(f"[ControlNet] Control image: {status.get('control_image_path', '')}")
        print(f"[ControlNet] Loaded: {status.get('loaded')}")
        print(f"[ControlNet] Fallback reason: {status.get('fallback_reason', '')}")
