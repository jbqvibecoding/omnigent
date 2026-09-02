#!/usr/bin/env python3
"""Extract the web UI's CSS custom properties into ``designs/UI/tokens.json``.

``web/src/index.css`` is the single source of truth for the palette. This script
mirrors it into JSON so design tooling can read the tokens without parsing CSS.
Run it after changing any token block:

    python3 designs/UI/extract_tokens.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CSS = REPO / "web" / "src" / "index.css"
OUT = REPO / "designs" / "UI" / "tokens.json"

# Selector -> (palette id, mode). Mirrors the `[data-theme]` blocks in index.css.
SELECTORS: dict[str, tuple[str, str]] = {
    ":root": ("omni", "light"),
    ".dark": ("omni", "dark"),
}
for palette_id in ("github", "catppuccin", "gruvbox", "dracula", "nord", "custom"):
    SELECTORS[f':root:not(.dark)[data-theme="{palette_id}"]'] = (palette_id, "light")
    SELECTORS[f'.dark[data-theme="{palette_id}"]'] = (palette_id, "dark")

DECL = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")


def declarations(body: str) -> dict[str, str]:
    """Return the custom properties declared in a rule body, whitespace-collapsed."""
    return {name: " ".join(value.split()) for name, value in DECL.findall(body)}


def main() -> None:
    text = CSS.read_text()
    # At-rule strings can contain `/*` (e.g. `@source ".../dist/*.js"`), which would
    # open a phantom comment and swallow everything after it — drop those lines
    # first, then strip real comments so `--foo: bar;` inside prose is never read
    # as a declaration.
    without_at_rules = re.sub(
        r"(?m)^\s*@(?:source|import|plugin|custom-variant)[^;]*;\s*$", "", text
    )
    stripped = re.sub(r"/\*.*?\*/", "", without_at_rules, flags=re.S)

    blocks: dict[str, str] = {}
    for match in re.finditer(r"(?m)^([^{}\n][^{}]*?)\{([^{}]*)\}", stripped):
        selector = " ".join(match.group(1).split())
        if selector in SELECTORS and selector not in blocks:
            blocks[selector] = match.group(2)

    palettes: dict[str, dict[str, dict[str, str]]] = {}
    for selector, (palette_id, mode) in SELECTORS.items():
        body = blocks.get(selector)
        if body is None:
            continue
        decls = declarations(body)
        if decls:
            palettes.setdefault(palette_id, {})[mode] = decls

    # `@theme inline` maps Tailwind utility names onto the tokens above.
    theme_block = re.search(r"@theme inline\s*\{(.*?)\n\}", stripped, flags=re.S)
    theme = declarations(theme_block.group(1)) if theme_block else {}

    # `.app-shell` canvas gradients, one per palette/mode.
    canvas: dict[str, dict[str, str]] = {}
    for match in re.finditer(
        r"(?m)^((?:\.dark)?[^{}\n]*\.app-shell)\s*\{(.*?)\n\}", stripped, flags=re.S
    ):
        selector = " ".join(match.group(1).split())
        value = re.search(r"background:\s*([^;]+);", match.group(2))
        if not value:
            continue
        mode = "dark" if selector.startswith(".dark") else "light"
        theme_attr = re.search(r'data-theme="([\w-]+)"', selector)
        palette_id = theme_attr.group(1) if theme_attr else "omni"
        canvas.setdefault(palette_id, {})[mode] = " ".join(value.group(1).split())

    payload = {
        "$comment": (
            "Generated from web/src/index.css by designs/UI/extract_tokens.py — "
            "edit the stylesheet, not this file."
        ),
        "source": "web/src/index.css",
        "tailwindTheme": theme,
        "palettes": palettes,
        "appShellCanvas": canvas,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}: {len(palettes)} palettes, {len(theme)} theme keys")


if __name__ == "__main__":
    main()
