import gradio as gr

from workflow.pipeline import MultimodalPipeline


def _empty_result(message):
    return (
        message,
        "",
        None,
        None,
        "",
        None,
        None,
        None,
        None,
        None,
        "",
    )


def _score(value):
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def _image_path(value):
    return value or None


def _agent_trace(value):
    if not isinstance(value, list):
        value = []
    return "\n".join(str(item) for item in value)


def run_workflow(image, user_prompt):
    print("[UI] Running multi-agent workflow...")

    if image is None:
        return _empty_result("Please upload an image before running the workflow.")

    try:
        pipeline = MultimodalPipeline()
        result = pipeline.run(image, user_prompt or "")

        agent_trace = _agent_trace(result.get("agent_trace", []))
        print("[UI] Workflow completed.")

        return (
            result.get("caption", ""),
            result.get("final_prompt", ""),
            _image_path(result.get("output_image_path")),
            _score(result.get("score")),
            result.get("reflection", ""),
            bool(result.get("retry_needed", False)),
            _image_path(result.get("retry_output_image_path")),
            _score(result.get("retry_score")),
            _image_path(result.get("best_output_image_path")),
            _score(result.get("best_score")),
            agent_trace,
        )
    except Exception as error:
        return _empty_result(f"Error: {error}")


def create_app():
    with gr.Blocks(title="Multi-Agent Image Workflow") as app:
        gr.Markdown("# Multi-Agent Image Workflow")

        with gr.Row():
            image_input = gr.Image(
                label="Image input",
                type="filepath",
            )
            user_prompt = gr.Textbox(
                label="User prompt",
                placeholder="e.g. anime style, cinematic lighting",
            )

        run_button = gr.Button("Run Multi-Agent Workflow")

        with gr.Row():
            caption = gr.Textbox(label="Caption")
            initial_score = gr.Number(label="Initial score")
            retry_needed = gr.Checkbox(label="Retry needed")
            retry_score = gr.Number(label="Retry score")
            best_score = gr.Number(label="Best score")

        final_prompt = gr.Textbox(label="Final prompt", lines=3)
        reflection = gr.Textbox(label="Reflection", lines=3)

        with gr.Row():
            initial_output_image = gr.Image(label="Initial output image")
            retry_output_image = gr.Image(label="Retry output image")
            best_output_image = gr.Image(label="Best output image")

        agent_trace = gr.Textbox(label="Agent trace", lines=8)

        run_button.click(
            fn=run_workflow,
            inputs=[image_input, user_prompt],
            outputs=[
                caption,
                final_prompt,
                initial_output_image,
                initial_score,
                reflection,
                retry_needed,
                retry_output_image,
                retry_score,
                best_output_image,
                best_score,
                agent_trace,
            ],
        )

    return app


def run():
    app = create_app()
    app.launch()
