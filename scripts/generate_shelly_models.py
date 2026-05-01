"""MkDocs hook: generate scripts/shelly_models.md from shelly_models.json."""
from __future__ import annotations

import json
from pathlib import Path

_JSON_PATH = Path("src/sc_smart_device/shelly_models.json")
_OUTPUT_PATH = Path("scripts/shelly_models.md")


def _pluralise(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _render_model(model: dict) -> str:
    name = model["name"]
    url = model["url"]
    model_id = model["model"]
    protocol = model["protocol"]
    inputs = model["inputs"]
    outputs = model["outputs"]
    meters = model["meters"]
    meters_seperate = model.get("meters_seperate", False)
    temp_monitoring = model.get("temperature_monitoring", False)

    if meters_seperate:
        meters_line = _pluralise(meters, "energy meter", "energy meters") + " (seperate from outputs)"
    elif meters > 0:
        meters_line = _pluralise(meters, "meter", "meters") + " (part of output)"
    else:
        meters_line = "0 meters"

    lines = [
        f"### [{name}]({url})",
        "",
        f"- Model ID: {model_id}",
        f"- Protocol: {protocol}",
        "- Components: ",
        f"    - {_pluralise(inputs, 'input', 'inputs')}",
        f"    - {_pluralise(outputs, 'output', 'outputs')}",
        f"    - {meters_line}",
        f"- Internal temperature monitoring: {'Yes' if temp_monitoring else 'No'}",
    ]
    return "\n".join(lines)


def _generate() -> str:
    models = json.loads(_JSON_PATH.read_text(encoding="utf-8"))

    by_generation: dict[int, list[dict]] = {}
    for model in models:
        gen = model["generation"]
        by_generation.setdefault(gen, []).append(model)

    sections: list[str] = []
    for gen in sorted(by_generation):
        sections.extend((f"## Generation {gen} Devices", ""))
        for model in by_generation[gen]:
            sections.extend((_render_model(model), ""))

    return "\n".join(sections).rstrip() + "\n"


def on_pre_build(config) -> None:  # noqa: ARG001
    _OUTPUT_PATH.write_text(_generate(), encoding="utf-8")
