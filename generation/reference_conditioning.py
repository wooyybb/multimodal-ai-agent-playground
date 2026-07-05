from generation.conditioning_package import default_conditioning_package


class ReferenceConditioningBuilder:
    def build(self, state: dict) -> dict:
        state = state or {}
        context_program = state.get("context_program") or {}
        reference_image = state.get("reference_image") or context_program.get("reference_image") or {}
        character_program = state.get("character_program") or context_program.get("character_program") or {}

        package = default_conditioning_package()
        package["reference_image_path"] = self._reference_image_path(state, reference_image)

        needs_preservation = self._needs_preservation(
            state,
            context_program,
            reference_image,
            character_program,
        )
        if needs_preservation:
            package.update(
                {
                    "enabled": True,
                    "conditioning_type": "ip_adapter_planned",
                    "identity_strength": 0.85,
                    "style_strength": 0.55,
                    "structure_strength": 0.45,
                }
            )
            package["notes"].append(
                "IP-Adapter hook planned; currently prompt-only fallback"
            )

        package["preserve"] = self._preserve_flags(reference_image, character_program)
        if not package["reference_image_path"]:
            package["notes"].append("reference image path unavailable")
        return package

    def _reference_image_path(self, state, reference_image):
        for value in (
            state.get("image"),
            state.get("reference_image_path"),
            reference_image.get("image_path") if isinstance(reference_image, dict) else None,
            reference_image.get("path") if isinstance(reference_image, dict) else None,
        ):
            if isinstance(value, str) and value:
                return value
        return ""

    def _needs_preservation(self, state, context_program, reference_image, character_program):
        text = " ".join(
            str(value or "").lower()
            for value in (
                state.get("generation_mode"),
                state.get("requested_provider"),
                state.get("provider"),
                state.get("user_prompt"),
                context_program.get("user_goal"),
                context_program.get("quality"),
            )
        )
        if any(keyword in text for keyword in ("quality", "identity", "preserve", "reference", "ip adapter")):
            return True
        if reference_image or character_program:
            return bool(state.get("image"))
        return False

    def _preserve_flags(self, reference_image, character_program):
        appearance = {}
        if isinstance(reference_image, dict):
            appearance.update(reference_image.get("appearance") or {})
        if isinstance(character_program, dict):
            appearance.update(character_program.get("appearance") or {})
        return {
            "hair": bool(appearance.get("hair") or appearance.get("hair_color")),
            "eye_color": bool(appearance.get("eye_color")),
            "outfit": bool(appearance.get("outfit")),
            "accessories": bool(appearance.get("accessories")),
            "silhouette": True,
        }
