from tools.blip_tool import BlipTool


class VisionAgent:
    def __init__(self, blip_tool=None):
        self.blip_tool = blip_tool or BlipTool()

    def run(self, image):
        print("[VisionAgent] Running...")
        caption = self.blip_tool.generate_caption(image)
        print(f"[VisionAgent] Caption: {caption}")
        return caption
