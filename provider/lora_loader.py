import os
from pathlib import Path


class LoRALoader:
    SUPPORTED = {
        "ghibli": "ghibli.safetensors",
        "anime": "anime.safetensors",
        "watercolor": "watercolor.safetensors",
        "realistic": "realistic.safetensors",
    }

    def load(self, pipeline, style_program: dict) -> dict:
        lora_name = str(style_program.get("lora_name") or "").lower()
        lora_scale = float(style_program.get("lora_scale") or 0.0)
        status = {
            "enabled": False,
            "selected_lora": lora_name,
            "lora_scale": lora_scale,
            "used_fallback": False,
            "reason": "LoRA disabled",
        }
        if not lora_name:
            return status
        if lora_name not in self.SUPPORTED:
            status["used_fallback"] = True
            status["reason"] = f"unsupported LoRA: {lora_name}"
            return status

        lora_path = self._lora_path(lora_name)
        if not lora_path.exists():
            status["used_fallback"] = True
            status["reason"] = f"LoRA file not found: {lora_path}"
            return status

        try:
            pipeline.load_lora_weights(str(lora_path.parent), weight_name=lora_path.name)
            if hasattr(pipeline, "set_adapters"):
                pipeline.set_adapters([lora_name], adapter_weights=[lora_scale])
            status["enabled"] = True
            status["reason"] = "LoRA loaded"
        except Exception as error:
            status["used_fallback"] = True
            status["reason"] = f"LoRA fallback: {error}"
        return status

    def _lora_path(self, lora_name):
        lora_dir = Path(os.getenv("LORA_DIR") or "models/lora")
        return lora_dir / self.SUPPORTED[lora_name]
