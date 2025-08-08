
# ai_story.py
import os, json, time, re
from typing import Dict, Any, List
import google.generativeai as genai

SCHEMA = {
    "id": str,
    "title": str,
    "text": str,
    "choices": list  # list of {id,label,effects,next?,repeatable?}
}

def _scene_id_from_position(pos: Dict[str, Any]) -> str:
    act = pos.get("act", 1)
    chap = pos.get("chapter", 1)
    base = pos.get("scene", f"act{act}_auto")
    # Ensure it's namespaced to the act
    if not base.startswith(f"act{act}_"):
        base = f"act{act}_{base}"
    return base

def _coerce_choice(c: Dict[str, Any]) -> Dict[str, Any]:
    # Normalize effects structure
    effects = c.get("effects") or {}
    out = {
        "id": str(c.get("id") or re.sub(r'[^a-z0-9_]+','_', c.get("label","")).lower()[:24] or "choice"),
        "label": str(c.get("label") or "Continue"),
        "repeatable": bool(c.get("repeatable", False)),
        "effects": {
            "stats": effects.get("stats") or {},
            "flags": effects.get("flags") or {},
            "relationships": effects.get("relationships") or {},
            "traits_add": effects.get("traits_add") or []
        },
        "next": c.get("next")  # may be None for AI mode
    }
    # Cast numeric deltas to int
    for k,v in list(out["effects"]["stats"].items()):
        try: out["effects"]["stats"][k] = int(v)
        except: out["effects"]["stats"][k] = 0
    for k,v in list(out["effects"]["relationships"].items()):
        try: out["effects"]["relationships"][k] = int(v)
        except: out["effects"]["relationships"][k] = 0
    return out

def _validate_scene(scene: Dict[str, Any]) -> Dict[str, Any]:
    # Basic validation and coercion
    sid = str(scene.get("id") or "act_auto_scene")
    title = str(scene.get("title") or sid.replace("_"," ").title())
    text = str(scene.get("text") or "")
    choices = scene.get("choices") or [{"label":"Continue","effects":{},"next":None}]
    norm = {
        "id": sid,
        "title": title,
        "text": text,
        "choices": [_coerce_choice(c) for c in choices]
    }
    return norm

def _build_prompt(state: Dict[str, Any], lore_snippets: str, memory_tail: str) -> str:
    position = state.get("position", {})
    stats = state.get("stats", {})
    flags = state.get("flags", {})
    relationships = state.get("relationships", {})
    traits = state.get("traits", {})

    return (
        "You are an expert interactive fiction generator for the Gelmark Engine. "
        "Output strictly in JSON with keys: id, title, text, choices[]. "
        "Choices must be a short list of 2-4 options with labels and simple effects deltas "
        "(stats {Strength:+1}, flags {seen_gate:true}, relationships {\"G.R.A.C.E.\":+1}). "
        "Never include markdown, only JSON. "
        "Honor these rules: stats cap 50; no death; failures branch without punishment; traits auto-slot; "
        "bosses scale by total stats every 5 points (mention narratively only if relevant). "
        "\n\n<position>"
        f"{json.dumps(position)}"
        "</position>\n<stats>"
        f"{json.dumps(stats)}"
        "</stats>\n<flags>"
        f"{json.dumps(flags)}"
        "</flags>\n<relationships>"
        f"{json.dumps(relationships)}"
        "</relationships>\n<traits>"
        f"{json.dumps(traits)}"
        "</traits>\n\n"
        "<lore>"
        f"{lore_snippets}"
        "</lore>\n<memory>"
        f"{memory_tail}"
        "</memory>\n\n"
        "Return a new scene that logically follows the position and lore. Keep text concise (120-220 words). "
        "Set id to a snake_case identifier starting with the current act, like 'act1_camp_gate' or 'act2_mines_intro'. "
    )

def _call_gemini(prompt: str) -> str:
    # Requires GEMINI_API_KEY in environment (already used by engine)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(prompt)
    return resp.text.strip()

def _extract_json_block(text: str) -> str:
    # Try fenced code first
    m = re.search(r"```json\s*([\s\S]+?)\s*```", text)
    if m: return m.group(1).strip()
    # Otherwise, best effort: find the first { .. } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text

def generate_scene(state: Dict[str, Any], lore_snap: Dict[str, str], memory_tail: str) -> Dict[str, Any]:
    """Generate a new scene dict using Gemini and return a validated scene."""
    lore_concat = "\n\n".join([f"--- {k} ---\n{v}" for k,v in lore_snap.items() if v])
    prompt = _build_prompt(state, lore_concat, memory_tail)
    raw = _call_gemini(prompt)
    json_str = _extract_json_block(raw)
    try:
        data = json.loads(json_str)
    except Exception:
        # Fallback minimal scene if model returns non-JSON
        pos = state.get("position", {})
        sid = _scene_id_from_position(pos) + "_auto"
        data = {
            "id": sid,
            "title": "A Fork in the Road",
            "text": "You steady your breath and take stock. Paths stretch forward; each promises risk and growth.",
            "choices": [
                {"label":"Advance cautiously","effects":{"stats":{"Insight":1}}},
                {"label":"Push yourself physically","effects":{"stats":{"Strength":1,"Endurance":1}}}
            ]
        }
    return _validate_scene(data)

