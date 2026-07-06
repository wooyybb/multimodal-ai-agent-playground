from dataclasses import asdict, dataclass, field


@dataclass
class GenerationPreset:
    preset_name: str
    sdxl_strength: float
    ip_adapter_scale: float
    cfg: float
    steps: int
    width: int = 768
    height: int = 768
    reason: str = ""
    environment_overrides: dict = field(default_factory=dict)

    @property
    def resolution(self):
        return f"{self.width}x{self.height}"

    def to_dict(self):
        data = asdict(self)
        data["resolution"] = self.resolution
        return data
