"""Shared state key constants for the orchestration boundary.

Keep this file focused on high-traffic keys. The goal is to reduce repeated
string literals at the framework edges without forcing a broad migration.
"""

IMAGE = "image"
USER_PROMPT = "user_prompt"
REQUESTED_PROVIDER = "requested_provider"
PROVIDER = "provider"
PLANNER_RESULT = "planner_result"
AGENT_TRACE = "agent_trace"

CAPTION = "caption"
FINAL_PROMPT = "final_prompt"
OUTPUT_IMAGE_PATH = "output_image_path"
SCORE = "score"
BEST_SCORE = "best_score"

STYLE_TRANSFER_PROGRAM = "style_transfer_program"
SEMANTIC_PROMPT_PROGRAM = "semantic_prompt_program"
GENERATION_RESULT = "generation_result"
EVALUATION_RESULT = "evaluation_result"
ADAPTIVE_PLAN = "adaptive_plan"
