from ui.app import create_app


if __name__ == "__main__":
    print("[UI] Launching Gradio app...")
    app = create_app()
    app.launch()
