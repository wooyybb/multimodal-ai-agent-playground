from agents.character_program_builder import CharacterProgramBuilder
from agents.reference_image_parser import ReferenceImageParser
from agents.vision_agent import VisionAgent


class UnderstandingAgent:
    """Facade for the v3 Understanding Agent module group."""

    modules = (VisionAgent, ReferenceImageParser, CharacterProgramBuilder)


__all__ = ["UnderstandingAgent"]
