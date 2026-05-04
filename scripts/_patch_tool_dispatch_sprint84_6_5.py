import re

with open("kernel/tool_dispatch.py", "r") as f:
    content = f.read()

# 1. Agregar ToolSpec a get_tool_specs()
tool_spec_code = """        ToolSpec(
            name="sovereign_browser_render",
            description=(
                "Renderiza una URL en un browser soberano (Playwright + Chromium "
                "dentro del kernel) y devuelve screenshot, HTML y Core Web Vitals "
                "(TTFB, LCP, load_time). Soporta viewport desktop o mobile."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL http:// o https:// a renderizar"},
                    "viewport_preset": {
                        "type": "string",
                        "enum": ["desktop", "mobile"],
                        "default": "desktop",
                    },
                    "full_page": {"type": "boolean", "default": True},
                    "capture_html": {"type": "boolean", "default": True},                    "capture_html": {"typered":                      },
            risk="low",
        ),
"""

if "name=\"sovereign_browser_render\"" not in content:
    # Insertar antes de browse_web
    content = content.replace('        ToolSpec(\n            name="browse_web",', tool_spec_code + '        ToolSpec(\n            name="browse_web",')

# 2. Agregar handler en tool_dispatch()
handler_code = """        elif tool_name == "sovereign_browser_render":
            from tools.sovereign_browser import sovereign_browser_render
            import json as _json
            
            result = await sovereign_browser_render(
                url=args.get("url", ""),
                viewport_preset=args.get("viewport_preset", "desktop"),
                full_page=args.get("full_page", True),
                capture_html=args.get("capture_html", True),
            )
            return _json.dumps(result)
"""

if "elif tool_name == \"sovereign_browser_render\":" not in content:
    content = content.replace('        elif tool_name == "browse_web":', handler_code + '        elif tool_name == "browse_web":')

with open("kernel/tool_dispatch.py", "w") as f:
    f.write(content)

print("Patch aplicado a kernel/tool_dispatch.py")
