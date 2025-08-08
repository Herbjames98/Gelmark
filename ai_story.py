
# ai_story.py — richer scene generator (drop-in)
import os, json, re, uuid, time
import google.generativeai as genai

MODEL_NAME = os.getenv("GELMARK_SCENE_MODEL", "gemini-2.5-flash")
TEMPERATURE = float(os.getenv("GELMARK_SCENE_TEMP", "0.9"))
TOP_P = float(os.getenv("GELMARK_SCENE_TOP_P", "0.95"))

STYLE_GUIDE = """
Write like a cinematic, grounded GM who shows instead of tells.
Use tight 2nd-person POV ("you") with occasional interior thoughts.
Keep sentences varied; mix short punchy prose with a few longer lines.
Always use concrete sensory detail (sound, smell, texture, temperature, light).
Let tiny actions do the work (hands, breath, footing, objects).
Include at least two pieces of diegetic dialogue or thoughts if natural—short and characterful.
Avoid filler like "you feel like", "suddenly", "very", "the air is thick with".
Avoid purple prose and cliché; pick one vivid metaphor max per scene.
Maintain continuity strictly: never contradict inventory, traits, flags, or prior scene.
Tone: moody, myth-tech, restrained awe; not jokey.
Paragraph target: 6–12 compact paragraphs (400–900 words), no bullet lists.
"""

CHOICE_RULES = """
Produce exactly FOUR grounded choices that flow from the scene.
Each choice should push a different play style: bold, cautious, clever, empathetic (or social).
Each choice should include a compact label (<=60 chars) and a one-line intent subtitle.
If the engine passed an 'effects' hint, attach a small JSON effects block: { "stats": {...}, "gold": int, "traits_add": [], "flags_set": {...} }.
Use only keys you need. Do not invent new stats or trait systems.
Do not end with "continue" or "next".
"""

TEMPLATE = """
You are the scene generator for an interactive fiction game, The Gelmark.
Follow the STYLE_GUIDE and CHOICE_RULES.

<CANON_LORE>
{lore}
</CANON_LORE>

<MEMORY_LOG>
{mem}
</MEMORY_LOG>

<CURRENT_STATE>
JSON describing the player state.
{state_json}
</CURRENT_STATE>

<PREVIOUS_SCENE>
{prev_summary}
</PREVIOUS_SCENE>

Write the next scene that logically follows. Respect act/chapter pacing if provided
(e.g., prologue -> Act 1 mining; later acts expand). Do NOT reset the story.

Return ONLY a JSON object with keys:
id, title, text, choices.
- id: string id that looks like "act{act}_step_{counter}_{slug}"
- title: 3–7 word evocative title
- text: the full scene prose (no markdown lists; newlines ok)
- choices: array of 4 objects: { "id": "a|b|c|d", "label": "...", "subtitle": "...", "effects": {...} }

Use single-line strings (no triple quotes) and escape newlines with \n.
"""

def _safe_slug(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:18] or "scene"

def generate_scene(live_state: dict, lore_snaps: dict, mem_tail: str, prev: dict=None):
    # Configure model (caller should have set genai.configure(api_key=...))
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(MODEL_NAME, generation_config={
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
    })

    act = int(((live_state.get("position") or {}).get("act") or 0))
    counter = int(live_state.get("scene_counter", 0)) + 1
    base_id = f"act{act}_step_{counter}_{uuid.uuid4().hex[:6]}"
    prev_summary = ""
    if prev:
        prev_summary = f"PrevTitle: {prev.get('prev_title','')}\nPrevChoice: {prev.get('choice_label','')}\nPrevText: {prev.get('prev_text','')[:900]}"

    prompt = TEMPLATE.format(
        lore=json.dumps(lore_snaps, ensure_ascii=False),
        mem=mem_tail or "",
        state_json=json.dumps(live_state, ensure_ascii=False),
        prev_summary=prev_summary
    ) + "\nSTYLE_GUIDE:\n" + STYLE_GUIDE + "\nCHOICE_RULES:\n" + CHOICE_RULES

    resp = model.generate_content(prompt)
    raw = resp.text.strip() if hasattr(resp, "text") else ""
    # Extract JSON object
    m = re.search(r"\{[\s\S]*\}\s*$", raw)
    if not m:
        raise RuntimeError("Model did not return JSON")
    data = json.loads(m.group(0))

    # Basic validation & normalization
    if not isinstance(data, dict): raise RuntimeError("Invalid scene JSON")
    sid = data.get("id") or base_id
    stitle = (data.get("title") or "A New Turn").strip()
    stext = (data.get("text") or "").strip()
    choices = data.get("choices") or []
    if len(choices) != 4:
        raise RuntimeError("Expected 4 choices")
    fixed = []
    for i, ch in enumerate(choices):
        cid = ch.get("id") or "abcd"[i]
        label = (ch.get("label") or "Decide").strip()[:60]
        subtitle = (ch.get("subtitle") or "").strip()
        effects = ch.get("effects") or {}
        fixed.append({"id": cid, "label": label, "subtitle": subtitle, "effects": effects})

    # Fallback title slug if needed
    slug = _safe_slug(stitle)
    sid = sid if sid.startswith("act") else f"act{act}_step_{counter}_{slug}"

    return {"id": sid, "title": stitle, "text": stext, "choices": fixed}
