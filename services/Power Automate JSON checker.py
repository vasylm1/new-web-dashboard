import html
import json
from dataclasses import dataclass

import streamlit as st

from translations import translations


VALID_STATUSES = {"Succeeded", "Failed", "Skipped", "TimedOut"}


@dataclass
class Finding:
    level: str
    message: str
    path: str = "$"
    line: int | None = None
    column: int | None = None


def _path(parent, key):
    return f"{parent}.{key}" if str(key).isidentifier() else f"{parent}[{key!r}]"


def _duplicate_keys(raw):
    duplicates = []

    def collect(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    json.loads(raw, object_pairs_hook=collect)
    return duplicates


def _definition(obj):
    if not isinstance(obj, dict):
        return None, "$"
    if isinstance(obj.get("definition"), dict):
        return obj["definition"], "$.definition"
    props = obj.get("properties")
    if isinstance(props, dict) and isinstance(props.get("definition"), dict):
        return props["definition"], "$.properties.definition"
    if "actions" in obj or "triggers" in obj:
        return obj, "$"
    return None, "$"


def _check_expression(value, path, findings):
    if not isinstance(value, str) or "@" not in value:
        return
    if value.count("@{") != value.count("}"):
        findings.append(Finding("error", "Unbalanced @{...} expression.", path))
    depth = 0
    quote = None
    for char in value:
        if quote:
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                findings.append(Finding("error", "Expression has an unexpected closing parenthesis.", path))
                return
    if depth:
        findings.append(Finding("error", "Expression has unbalanced parentheses.", path))


def _walk_expressions(value, path, findings):
    if isinstance(value, dict):
        for key, child in value.items():
            _walk_expressions(child, _path(path, key), findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_expressions(child, f"{path}[{index}]", findings)
    else:
        _check_expression(value, path, findings)


def _check_actions(actions, path, findings):
    if not isinstance(actions, dict):
        findings.append(Finding("error", "Actions must be a JSON object.", path))
        return
    names = set(actions)
    for name, action in actions.items():
        action_path = _path(path, name)
        if not isinstance(action, dict):
            findings.append(Finding("error", "Action must be a JSON object.", action_path))
            continue
        if not isinstance(action.get("type"), str) or not action["type"].strip():
            findings.append(Finding("error", "Action is missing a non-empty type.", action_path))
        run_after = action.get("runAfter")
        if run_after is not None:
            if not isinstance(run_after, dict):
                findings.append(Finding("error", "runAfter must be a JSON object.", _path(action_path, "runAfter")))
            else:
                for dependency, statuses in run_after.items():
                    dep_path = _path(_path(action_path, "runAfter"), dependency)
                    if dependency not in names:
                        findings.append(Finding("error", f"runAfter references unknown action '{dependency}'.", dep_path))
                    if not isinstance(statuses, list) or not statuses:
                        findings.append(Finding("error", "runAfter statuses must be a non-empty array.", dep_path))
                    else:
                        unknown = [status for status in statuses if status not in VALID_STATUSES]
                        if unknown:
                            findings.append(Finding("warning", f"Unknown runAfter status: {', '.join(map(str, unknown))}.", dep_path))
        for branch in ("actions",):
            if branch in action:
                _check_actions(action[branch], _path(action_path, branch), findings)
        cases = action.get("cases")
        if isinstance(cases, dict):
            for case_name, case in cases.items():
                if isinstance(case, dict) and "actions" in case:
                    _check_actions(case["actions"], _path(_path(_path(action_path, "cases"), case_name), "actions"), findings)
        default = action.get("default")
        if isinstance(default, dict) and "actions" in default:
            _check_actions(default["actions"], _path(_path(action_path, "default"), "actions"), findings)


def validate(raw):
    findings = []
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        findings.append(Finding("error", exc.msg, "$", exc.lineno, exc.colno))
        return None, findings

    for key in sorted(set(_duplicate_keys(raw))):
        findings.append(Finding("error", f"Duplicate key '{key}' overwrites an earlier value."))

    if not isinstance(obj, dict):
        findings.append(Finding("error", "The root value must be a JSON object."))
        return obj, findings

    definition, definition_path = _definition(obj)
    if definition is None:
        findings.append(Finding("warning", "Valid JSON, but no Power Automate definition was found."))
        _walk_expressions(obj, "$", findings)
        return obj, findings

    triggers = definition.get("triggers")
    if triggers is None:
        findings.append(Finding("error", "Flow definition is missing triggers.", definition_path))
    elif not isinstance(triggers, dict) or not triggers:
        findings.append(Finding("error", "triggers must be a non-empty JSON object.", _path(definition_path, "triggers")))
    else:
        for name, trigger in triggers.items():
            if not isinstance(trigger, dict) or not isinstance(trigger.get("type"), str):
                findings.append(Finding("error", "Trigger is missing a type.", _path(_path(definition_path, "triggers"), name)))

    actions = definition.get("actions")
    if actions is None:
        findings.append(Finding("error", "Flow definition is missing actions.", definition_path))
    else:
        _check_actions(actions, _path(definition_path, "actions"), findings)

    _walk_expressions(definition, definition_path, findings)
    return obj, findings


def _source_view(raw, line):
    rows = []
    for number, text in enumerate(raw.splitlines(), 1):
        marked = number == line
        bg = "#fee2e2" if marked else "transparent"
        color = "#991b1b" if marked else "#334155"
        rows.append(
            f'<div style="display:flex;background:{bg};color:{color};">'
            f'<span style="width:48px;flex:none;padding:2px 10px;text-align:right;'
            f'color:#94a3b8;user-select:none">{number}</span>'
            f'<span style="white-space:pre-wrap;padding:2px 10px">{html.escape(text) or " "}</span></div>'
        )
    return (
        '<div style="font:13px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace;'
        'border:1px solid #e2e8f0;border-radius:12px;overflow:auto;max-height:420px;'
        'background:#fff">' + "".join(rows) + "</div>"
    )


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["paj_title"])
    st.caption(t["paj_intro"])
    raw = st.text_area(t["paj_input"], height=330, placeholder='{"properties":{"definition":{"triggers":{},"actions":{}}}}')

    if not st.button(t["paj_check"], width="stretch"):
        return
    if not raw.strip():
        st.warning(t["paj_empty"])
        return

    obj, findings = validate(raw)
    errors = [item for item in findings if item.level == "error"]
    warnings = [item for item in findings if item.level == "warning"]

    c1, c2 = st.columns(2)
    c1.metric(t["paj_errors"], len(errors))
    c2.metric(t["paj_warnings"], len(warnings))
    if errors:
        st.error(t["paj_invalid"])
    elif warnings:
        st.warning(t["paj_valid_warnings"])
    else:
        st.success(t["paj_valid"])

    for item in findings:
        location = item.path
        if item.line is not None:
            location += f" · {t['paj_line']} {item.line}, {t['paj_column']} {item.column}"
        message = f"**{location}**: {item.message}"
        st.error(message) if item.level == "error" else st.warning(message)

    syntax_line = next((item.line for item in errors if item.line is not None), None)
    if syntax_line:
        st.subheader(t["paj_source"])
        st.markdown(_source_view(raw, syntax_line), unsafe_allow_html=True)
    elif obj is not None:
        formatted = json.dumps(obj, ensure_ascii=False, indent=2)
        st.subheader(t["paj_formatted"])
        st.code(formatted, language="json")
        st.download_button(
            "⬇️ " + t["paj_download"],
            formatted,
            file_name="power-automate-flow.json",
            mime="application/json",
        )
