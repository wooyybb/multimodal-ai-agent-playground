from tools.vlm.vlm_router import VLMRouter


class CaptionResult(str):
    def __new__(cls, caption, vision_result=None):
        obj = str.__new__(cls, caption)
        obj.vision_result = vision_result or {}
        return obj

    def __getitem__(self, key):
        return self.to_dict()[key]

    def get(self, key, default=None):
        return self.to_dict().get(key, default)

    def to_dict(self):
        return {
            "caption": str(self),
            "vision_result": self.vision_result,
        }


class VisionAgent:
    def __init__(self, vlm_router=None):
        self.vlm_router = vlm_router or VLMRouter()

    def run(self, image):
        print("[VisionAgent] Running...")
        vlm = self.vlm_router.select()
        vision_result = vlm.analyze(image)
        caption = vision_result.get("caption", "")
        print(f"[VisionAgent] Provider: {vision_result.get('provider')}")
        print(f"[VisionAgent] Fallback: {vision_result.get('used_fallback')}")
        print(f"[VisionAgent] Latency: {vision_result.get('latency')}s")
        print(f"[VisionAgent] Caption: {caption}")
        print(f"[VisionAgent] Detailed Caption: {vision_result.get('detailed_caption', '')}")
        print(f"[VisionAgent] Objects: {len(vision_result.get('objects') or [])}")
        return CaptionResult(caption, vision_result)
