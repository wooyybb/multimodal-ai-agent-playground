class PromptAgent:
    def run(self, caption: str, user_prompt: str) -> str:
        print("[PromptAgent] Running...")
        print(f"[PromptAgent] Caption: {caption}")
        print(f"[PromptAgent] User Prompt: {user_prompt}")

        base_prompt = (
            f"high quality, detailed image of {caption}, cinematic lighting"
        )

        if user_prompt.strip():
            final_prompt = f"{base_prompt}, user request: {user_prompt.strip()}"
        else:
            final_prompt = base_prompt

        print(f"[PromptAgent] Final Prompt: {final_prompt}")
        return final_prompt
