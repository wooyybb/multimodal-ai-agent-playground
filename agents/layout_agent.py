class LayoutAgent:
    def run(self, user_prompt: str, planner_result: dict | None = None) -> dict:
        print("[LayoutAgent] Planning layout...")
        text = str(user_prompt or "").lower()
        layout_type = self._detect_layout_type(text)
        camera_view = self._detect_camera_view(text)
        subject_placement = self._detect_subject_placement(text)

        plan = {
            "layout_type": layout_type,
            "aspect_ratio": self._aspect_ratio(layout_type, text),
            "frame_structure": self._frame_structure(layout_type, text),
            "camera_view": camera_view,
            "subject_placement": subject_placement,
            "background_style": self._background_style(layout_type, text),
            "composition_rules": self._composition_rules(layout_type),
        }

        print(f"[LayoutAgent] Layout Type: {plan['layout_type']}")
        print(f"[LayoutAgent] Camera: {plan['camera_view']}")
        print(f"[LayoutAgent] Subject Placement: {plan['subject_placement']}")
        print(f"[LayoutAgent] Composition Rules: {plan['composition_rules']}")
        return plan

    def _detect_layout_type(self, text):
        for layout_type in (
            "photobooth",
            "scrapbook",
            "poster",
            "profile",
            "portrait",
            "illustration",
            "sticker_sheet",
            "concept_sheet",
            "comic_page",
            "cinematic",
        ):
            if layout_type.replace("_", " ") in text or layout_type in text:
                return layout_type
        if "4-panel" in text or "four panel" in text:
            return "photobooth"
        if "comic" in text:
            return "comic_page"
        if "sticker" in text:
            return "sticker_sheet"
        return "illustration"

    def _detect_camera_view(self, text):
        camera_options = (
            "front",
            "eye_level",
            "slightly_above",
            "wide",
            "close_up",
            "medium",
            "full_body",
            "half_body",
        )
        for option in camera_options:
            if option.replace("_", " ") in text or option in text:
                return option
        if "portrait" in text:
            return "medium"
        if "full body" in text:
            return "full_body"
        if "close" in text:
            return "close_up"
        return "eye_level"

    def _detect_subject_placement(self, text):
        for placement in (
            "centered",
            "rule_of_thirds",
            "symmetrical",
            "diagonal",
            "balanced",
        ):
            if placement.replace("_", " ") in text or placement in text:
                return placement
        if "poster" in text or "profile" in text:
            return "centered"
        return "balanced"

    def _aspect_ratio(self, layout_type, text):
        if "vertical" in text or layout_type in ("photobooth", "portrait", "poster"):
            return "vertical"
        if layout_type in ("comic_page", "scrapbook"):
            return "page layout"
        if layout_type == "cinematic":
            return "wide cinematic"
        return "flexible"

    def _frame_structure(self, layout_type, text):
        if layout_type == "photobooth":
            return "4 connected vertical frames"
        if layout_type == "comic_page":
            return "multiple panels with clear separation"
        if layout_type == "sticker_sheet":
            return "separate sticker poses on one sheet"
        if layout_type == "concept_sheet":
            return "organized character reference sections"
        if "4-panel" in text or "four panel" in text:
            return "4 connected frames"
        return "single clear frame"

    def _background_style(self, layout_type, text):
        if layout_type == "photobooth":
            return "minimal scrapbook paper"
        if layout_type == "scrapbook":
            return "pastel scrapbook decorations"
        if layout_type == "poster":
            return "clean background"
        if layout_type == "comic_page":
            return "panel-friendly background with speech balloon space"
        if "clean" in text:
            return "clean minimal background"
        return "subtle background with low distraction"

    def _composition_rules(self, layout_type):
        rules_by_type = {
            "photobooth": [
                "4 connected frames",
                "consistent camera",
                "minimal spacing",
                "natural snapshot feeling",
                "balanced subject placement",
            ],
            "poster": [
                "large hero subject",
                "strong visual hierarchy",
                "clean background",
                "focus on center",
            ],
            "comic_page": [
                "multiple panels",
                "reading flow",
                "speech balloon space",
                "clear separation",
            ],
            "scrapbook": [
                "layered paper composition",
                "soft decorative spacing",
                "clear subject focus",
            ],
            "sticker_sheet": [
                "separate silhouettes",
                "even spacing",
                "clear cutout shapes",
            ],
            "cinematic": [
                "strong depth",
                "clear focal point",
                "controlled negative space",
            ],
        }
        return rules_by_type.get(
            layout_type,
            ["clear focal point", "balanced subject placement", "avoid awkward cropping"],
        )
