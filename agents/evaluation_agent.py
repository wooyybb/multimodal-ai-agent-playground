from tools.clip_tool import ClipTool


class EvaluationAgent:
    def __init__(self, clip_tool=None):
        self.clip_tool = clip_tool or ClipTool()

    def run(self, reference_image, generated_image_path, final_prompt) -> float:
        print("[EvaluationAgent] Running...")
        score = self.clip_tool.evaluate(
            reference_image,
            generated_image_path,
            final_prompt,
        )
        print(f"[EvaluationAgent] Score: {score}")
        return score
