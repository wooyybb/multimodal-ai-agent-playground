class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, callable_obj):
        print(f"[ToolRegistry] Registering tool: {name}")
        self._tools[name] = callable_obj

    def call(self, name: str, *args, **kwargs):
        print(f"[ToolRegistry] Calling tool: {name}")

        if name not in self._tools:
            raise ValueError(f"Tool is not registered: {name}")

        tool = self._tools[name]
        if hasattr(tool, "run"):
            return tool.run(*args, **kwargs)
        if callable(tool):
            return tool(*args, **kwargs)

        raise ValueError(f"Registered tool is not callable: {name}")

    def run_with_state(self, name: str, state: dict) -> dict:
        print(f"[ToolRegistry] Running state-based tool: {name}")

        if name not in self._tools:
            raise ValueError(f"Tool is not registered: {name}")

        tool = self._tools[name]
        if hasattr(tool, "run"):
            result = tool.run(state)
        elif callable(tool):
            result = tool(state)
        else:
            raise ValueError(f"Registered tool is not callable: {name}")

        if result is None:
            result = {}
        if not isinstance(result, dict):
            print(
                f"[ToolRegistry] Warning: {name} returned "
                f"{type(result).__name__}; wrapping result."
            )
            result = {name: result}

        print(f"[ToolRegistry] State update keys: {list(result.keys())}")
        return result

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        return name in self._tools
