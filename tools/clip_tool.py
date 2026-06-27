from pathlib import Path


class ClipTool:
    def evaluate(self, reference_image, generated_image_path, final_prompt) -> float:
        print("[CLIP] Evaluating mock similarity...")

        generated_exists = Path(generated_image_path).exists()
        prompt_length = len(final_prompt.strip())

        base_score = 0.45
        file_bonus = 0.25 if generated_exists else 0.0
        prompt_bonus = min(prompt_length / 400, 0.30)

        return round(min(base_score + file_bonus + prompt_bonus, 1.0), 3)
