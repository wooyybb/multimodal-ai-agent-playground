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

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        return name in self._tools
