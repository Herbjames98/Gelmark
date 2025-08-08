
# ai_story.py (clean, robust)
import os
import re
import json
from typing import Dict, Any, Optional
import google.generativeai as genai

# ---------- Helpers ----------

def _scene_id_from_position(pos: Dict[str, Any]) -> str:
    act = pos.get("act", 1) or 1
    base = pos.get("scene", f"act{act}_auto")
    base = str(base)
    if not base.startswith(f"act{act}_") and not base.startswith("prologue_"):
        base = f"act{act}_" + base
    return base

def _coerce_choice(c: Dict[str, Any]) -> Dict[str, Any]:
    label = str(c.get("label", "Continue"))
    effects = c.get("effects") or {}
    out = {
        "id": re.sub(r"[^a-z0-9_]+", "_", label.lower())[:24] or "choice",
        "label": label,
        "repeatable": bool(c.get("repeatable", False)),
        "effects": {
            "stats": effects.get("stats") or {},
            "flags": effects.get("flags") or {},
            "relationships": effects.get("relationships") or {},
            "traits_add": effects.get("traits_add") or []
        },
        "next": None
    }
    # Cast numeric deltas to ints
    for k, v in list(out["effects"]["stats"].items()):
        try:
            out["effects"]["stats"][k] = int(v)
        except Exception:
            out["effects"]["stats"][k] = 0
    for k, v in list(out["effects"]["relationships"].items()):
        try:
            out["effects"]["relationships"][k] = int(v)
        except Exception:
            out["effects"]["relationships"][k] = 0
    return out

def _validate_scene(scene: Dict[str, Any]) -> Dict[str, Any]:
    sid = str(scene.get("id", "act_auto_scene"))
    title = str(scene.get("title", sid.replace("_", " ").title()))
    text = str(scene.get("text", ""))
    raw_choices = scene.get("choices") or []
    choices = [_coerce_choice(c) for c in raw_choices]

    # Guarantee exactly 4 choices
    while len(choices) < 4:
        choices.append(_coerce_choice({"label": f"Option {len(choices)+1}", "effects": {}}))
    if len(choices) > 4:
        choices = choices[:4]

    return {"id": sid, "title": title, "text": text, "choices": choices}

def _build_prompt(state: Dict[str, Any], lore_snippets: str, memory_tail: str, prev: Optional[Dict[str, Any]]) -> str:
    position = state.get("position", {})
    stats = state.get("stats", {})
    flags = state.get("flags", {})
    relationships = state.get("relationships", {})
    traits = state.get("traits", {})

    prompt = (
        "You are an interactive fiction generator for the Gelmark Engine. "
        "Return STRICT JSON with keys: id, title, text, choices[]. "
        "Return EXACTLY 4 choices. Each choice needs: label (2-6 words), "
        "effects {stats, flags, relationships, traits_add}. "
        "Do NOT include any 'next' fields, markdown, code fences, or commentary. "
        "Honor rules: stats cap 50; repeatable training ok; no death; failures branch narratively; "
        "traits auto-slot; bosses scale by total stats every 5 points (mention only if relevant).\n"
        "<position>" + json.dumps(position) + "</position>\n"
        "<stats>" + json.dumps(stats) + "</stats>\n"
        "<flags>" + json.dumps(flags) + "</flags>\n"
        "<relationships>" + json.dumps(relationships) + "</relationships>\n"
        "<traits>" + json.dumps(traits) + "</traits>\n"
        "<lore>\n" + lore_snippets + "\n</lore>\n"
        "<memory>\n" + memory_tail + "\n</memory>\n"
    )
    if prev:
        prompt += "<previous_scene>" + json.dumps(prev, ensure_ascii=False) + "</previous_scene>\n"
        prompt += ("Continue directly from <previous_scene>. Reference what the player just did. "
                   "Keep location continuity unless a choice clearly moves the scene. ")
    prompt += ("Keep the main text concise (120-220 words). "
               "If the current act is 0, start scene id with 'prologue_'; else use 'actN_' where N is the act.")
    return prompt

def _call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()
    return text

def _extract_candidate(text: str) -> str:
    m = re.search(r"```json\s*([\s\S]+?)\s*```", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"```[\w]*\s*([\s\S]+?)\s*```", text)
    if m:
        return m.group(1).strip()
    start = text.find("{"); end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text.strip()

def _json_cleanup(s: str) -> str:
    # Remove comments
    s = re.sub(r"//.*?$|/\*.*?\*/", "", s, flags=re.M | re.S)
    # Normalize quotes
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    # Convert single-quoted to double if no double quotes present
    if "'" in s and s.count('"') == 0:
        s = re.sub(r"'([^']*)'", lambda m: '"' + m.group(1).replace('"', '\"') + '"', s)
    # True/False/None -> json
    s = re.sub(r"\bTrue\b", "true", s)
    s = re.sub(r"\bFalse\b", "false", s)
    s = re.sub(r"\bNone\b", "null", s)
    # Remove leading + from numbers
    s = re.sub(r":\s*\+(\d+)", r": \1", s)
    # Trailing commas
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s

def _safe_parse(text: str) -> Dict[str, Any]:
    cand = _extract_candidate(text)
    try:
        return json.loads(cand)
    except Exception:
        pass
    cleaned = _json_cleanup(cand)
    try:
        return json.loads(cleaned)
    except Exception:
        # Final fallback scene
        return {
            "id": "prologue_emergency_path",
            "title": "Gather Yourself",
            "text": "You breathe in the smoke and think clearly. Four paths present themselves, each a different way to move forward.",
            "choices": [
                {"label": "Scout the corridor", "effects": {"stats": {"Insight": 1}}},
                {"label": "Salvage fallen gear", "effects": {"stats": {"Dexterity": 1}}},
                {"label": "Call to G.R.A.C.E.", "effects": {"relationships": {"G.R.A.C.E.": 1}}},
                {"label": "Push through rubble", "effects": {"stats": {"Strength": 1, "Endurance": 1}}}
            ]
        }

# ---------- Public API ----------

def generate_scene(state: Dict[str, Any], lore_snap: Dict[str, str], memory_tail: str, prev: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    lore_concat = "\n\n".join([f"--- {k} ---\n{v}" for k, v in lore_snap.items() if v])
    prompt = _build_prompt(state, lore_concat, memory_tail, prev)
    raw = _call_gemini(prompt)
    data = _safe_parse(raw)
    return _validate_scene(data)

