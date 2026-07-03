# Demo Script

## One-Minute Explanation

This project is a multimodal AI agent framework for image generation. A user uploads an image and writes a request. The system captions the image, retrieves memory and style context, plans the scene, builds a context program, assembles and optimizes prompts, routes to a provider, generates an image, evaluates it with CLIP, reflects on the result, retries if needed, and saves memory plus debug reports.

## Demo Flow

1. Run `python main.py`.
2. Upload an image.
3. Enter a user prompt.
4. Run the workflow.
5. Show generated image, score, retry result, agent trace, and debug report path.

## Codex Usage

Codex was used sprint-by-sprint with strict workspace and allowed-file rules. The human defined architecture goals and reviewed results; Codex helped implement and document scoped changes.

## Future Work

- Add curated demo screenshots under `assets/demo/`.
- Add a two-minute technical walkthrough.
