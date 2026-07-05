class ControlNetHook:
    SUPPORTED = {"openpose", "depth", "canny"}

    def prepare(self, plan: dict, state: dict) -> dict:
        controlnet = (plan or {}).get("controlnet") or {}
        control_type = str(controlnet.get("type") or "none").lower()
        enabled = bool(controlnet.get("enabled"))
        status = {
            "enabled": False,
            "type": control_type,
            "used_fallback": False,
            "reason": controlnet.get("reason") or "ControlNet disabled",
        }
        if not enabled or control_type == "none":
            return status
        if control_type not in self.SUPPORTED:
            status["used_fallback"] = True
            status["reason"] = f"unsupported ControlNet type: {control_type}"
            return status

        status["used_fallback"] = True
        status["reason"] = (
            f"ControlNet {control_type} hook planned; control image/model not connected"
        )
        return status
