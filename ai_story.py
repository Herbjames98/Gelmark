# ai_story.py — robust scene generator (drop-in)
import os, json, re, uuid
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
Include at least two bits of diegetic dialogue (short, characterful) if natural.
Avoid filler like "you feel like", "suddenly", "very", "the air is thick with".
Avoid purple prose and cliché; one vivid metaphor max per scene.
Maintain continuity strictly: never contradict inventory, traits, flags, or prior scene.
Tone: moody, myth-tech, restrained awe; not jokey.
Paragraph target: 6–12 compact paragraphs (400–900 words), no bullet lists.
"""

CHOICE_RULES = """
Produce exactly FOUR grounded choices that flow from the scene.
Each choice should push a different style: bold, cautious, clever, empathetic (or social).
Each choice must include: { "id": "a|b|c|d", "label": "...", "subtitle": "...", "effects": {...} }.
If the engine passed an 'effects' hint, include it minimally (only keys you use).
Do not invent new stats or systems.
Avoid generic labels like "Continue" or "Next".
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

def _safe_slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:18] or "scene"

def _pad_to_four(choices):
    # Normalize and pad/truncate to exactly 4 choices
    base_ids = ["a", "b", "c", "d"]
    fixed = []
    for i in range(min(4, len(choices or []))):
        ch = choices[i] or {}
        cid = (ch.get("id") or base_ids[i])[:8]
        label = (ch.get("label") or "Decide").strip()[:60]
        subtitle = (ch.get("subtitle") or "").strip()
        eff = ch.get("effects") or {}
        fixed.append({"id": cid, "label": label, "subtitle": subtitle, "effects": eff})
    # Pad if less than 4
    for i in range(len(fixed), 4):
        fixed.append({
            "id": base_ids[i],
            "label": f"Improvise ({base_ids[i]})",
            "subtitle": "Make a fast call and adapt.",
            "effects": {}
        })
    return fixed[:4]

def _fallback_scene(live_state, counter):
    # Deterministic emergency scene if model fails
    act = int(((live_state.get("position") or {}).get("act") or 0))
    title = "Breath in the Ozone"
    text = (
        "Static crawls over your forearms as the corridor lights stutter. You steady yourself against the warm bulkhead; "
        "the metal vibrates like a sleeping animal. Far down the spine of the ruin, the GG stencils arrow toward a service hatch.\n\n"
        "G.R.A.C.E. flickers at your shoulder—one bright blink, then two. '...route...stable...' she whispers, a broken reed. "
        "You draw a slow breath. Dust tastes like old batteries. Somewhere, coolant drips in a slow, miserly rhythm."
    )
    slug = _safe_slug(title)
    sid = f"act{act}_step_{counter}_{slug}"
    choices = _pad_to_four([
        {"id":"a","label":"Follow the GG arrows","subtitle":"Trust GelCap signage toward the hatch","effects":{"stats":{"Focus":1}}},
        {"id":"b","label":"Pry open a side panel","subtitle":"Scavenge parts to MacGyver a tool","effects":{"stats":{"Strength":1}}}, 
        {"id":"c","label":"Ping G.R.A.C.E. diagnostics","subtitle":"Stabilize her output before moving","effects":{"stats":{"Focus":1},"flags_set":{"grace_stable":True}}},
        {"id":"d","label":"Listen before you move","subtitle":"Map the space by sound, stay low","effects":{"stats":{"Speed":1}}}
    ])
    return {"id": sid, "title": title, "text": text, "choices": choices, "act": act}

def generate_scene(live_state: dict, lore_snaps: dict, mem_tail: str, prev: dict=None):
    # Configure model
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    act = int(((live_state.get("position") or {}).get("act") or 0))
    counter = int(live_state.get("scene_counter", 0)) + 1

    prev_summary = ""
    if prev:
        prev_summary = f"PrevTitle: {prev.get('prev_title','')}\nPrevChoice: {prev.get('choice_label','')}\nPrevText: {prev.get('prev_text','')[:900]}"

    prompt = TEMPLATE.format(
        lore=json.dumps(lore_snaps, ensure_ascii=False),
        mem=mem_tail or "",
        state_json=json.dumps(live_state, ensure_ascii=False),
        prev_summary=prev_summary
    ) + "\nSTYLE_GUIDE:\n" + STYLE_GUIDE + "\nCHOICE_RULES:\n" + CHOICE_RULES

    # Try the model; fall back to deterministic scene if anything goes wrong
    try:
        model = genai.GenerativeModel(MODEL_NAME, generation_config={"temperature": TEMPERATURE, "top_p": TOP_P})
        resp = model.generate_content(prompt)
        raw = (getattr(resp, "text", None) or "").strip()
        m = re.search(r"\{[\s\S]*\}\s*$", raw)
        if not m:
            raise RuntimeError("Model did not return JSON")
        data = json.loads(m.group(0))
        if not isinstance(data, dict):
            raise RuntimeError("Invalid scene JSON")

        # Normalize
        title = (data.get("title") or "A New Turn").strip()
        text = (data.get("text") or "").strip()
        choices = _pad_to_four(data.get("choices") or [])
        # slug + id
        slug = _safe_slug(title)
        sid = data.get("id") or f"act{act}_step_{counter}_{slug}"
        if not sid.startswith("act"):
            sid = f"act{act}_step_{counter}_{slug}"

        scene = {"id": sid, "title": title, "text": text, "choices": choices, "act": act}
        return scene

    except Exception:
        # Guaranteed, valid fallback
        return _fallback_scene(live_state, counter)
