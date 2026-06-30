class LayoutAgent:
    def run(self, user_prompt: str, planner_result: dict | None = None) -> dict:
        print("[LayoutAgent] Running...")
        text = str(user_prompt or "").lower()
        layout = "balanced image composition"
        frame_structure = "single clean frame"
        background = "clean background with subtle visual detail"

        if "photobooth" in text:
            layout = "vertical Korean photobooth memory collage"
        if "4-panel" in text or "four panel" in text:
            frame_structure = "4 connected vertical frames"
        if "vertical" in text:
            frame_structure = "vertical strip composition"
        if "scrapbook" in text:
            background = "clean white paper with minimal pastel scrapbook decorations"

        return {
            "layout": layout,
            "frame_structure": frame_structure,
            "background": background,
        }
