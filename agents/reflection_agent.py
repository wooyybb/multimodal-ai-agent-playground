class ReflectionAgent:
    def __init__(self, threshold=0.75):
        self.threshold = threshold

    def run(self, caption, final_prompt, score) -> dict:
        print("[ReflectionAgent] Running...")

        if score < self.threshold:
            suggested_prompt = (
                f"{final_prompt}, clearer subject details, stronger composition, "
                f"more faithful to the caption: {caption}"
            )
            return {
                "reflection": (
                    "Score is below threshold. Improve subject clarity, "
                    "composition, and alignment with the original caption."
                ),
                "suggested_prompt": suggested_prompt,
                "needs_retry": True,
            }

        return {
            "reflection": "no major revision needed",
            "suggested_prompt": final_prompt,
            "needs_retry": False,
        }
