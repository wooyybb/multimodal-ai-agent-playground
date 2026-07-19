from registry.tool_catalog import ToolCatalog


def test_tool_catalog_exposes_only_allowlisted_aliases():
    catalog = ToolCatalog()
    aliases = set(catalog.aliases())

    assert "understand_reference" in aliases
    assert "generate_sdxl_with_ip_adapter" in aliases
    assert "aggregate_evaluation" in aliases
    assert "shell" not in aliases
    assert "delete_workspace" not in aliases


def test_catalog_public_schema_does_not_expose_callables():
    catalog = ToolCatalog()
    public_tools = catalog.tools_for_llm()

    assert public_tools
    assert all("actual_steps" not in item for item in public_tools)
    assert all("description" in item for item in public_tools)
    assert all("agent_group" in item for item in public_tools)
