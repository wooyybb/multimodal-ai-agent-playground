from modules.understanding.character_program_builder import CharacterProgramBuilder
from modules.understanding.reference_image_parser import ReferenceImageParser
from modules.understanding.vision_agent import VisionAgent


class UnderstandingAgent:
    """Facade for the v3 Understanding Agent module group."""

    modules = (VisionAgent, ReferenceImageParser, CharacterProgramBuilder)


__all__ = ["UnderstandingAgent"]
