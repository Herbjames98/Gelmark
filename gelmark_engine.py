# This is the Gelmark Engine V6: The final, definitive version.
# It uses the correct Gemini 2.5 Pro model and is self-contained for reliability.

import streamlit as st
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- THIS IS THE BULLETPROOF .ENV FIX ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(dotenv_path=DOTENV_PATH)
# --- END OF FIX ---

# --- Configuration ---
st.set_page_config(page_title="Gelmark Engine", layout="wide")


# --- GAME DATABASE (All your lore and stats are stored here directly) ---

PLAYER_STATE = {
    "profile": {
        "name_title": "Askr, the Valking",
        "current_arc_act": "Act 3, Chapter 1: Echo Chamber",
        "origin_class_lineage": "Human, Time-Sent Survivor, Valking Initiate",
        "covenant_oath": "Vow to awaken the Frozen King."
    },
    "stats": {
        "Strength": 15,
        "Dexterity": 10,
        "Insight": 10,
        "Focus": 12,
        "Charisma": 1,
        "Resolve": 14,
        "Spirit": 10,
        "Agility": 12,
        "Willpower": 10,
        "Lore": 10
    },
    "traits": {
        "active": [
            "Mines-Forged",
            "Commandless Grace"
        ],
        "echoform": [],
        "fused": []
    },
    "inventory": {
        "relics": [],
        "key_items": [
            "Makeshift Charger",
            "Whisper-Etched Rune"
        ],
        "equipment": {
            "weapon": "Valking's Axe",
            "armor": "Reinforced Hide Armor"
        }
    },
    "companions": [
        {
            "name": "G.R.A.C.E.",
            "sync": "50%",
            "status": "Partial reactivation; ancient records accessible."
        }
    ]
}

LORE_DATA = {
    "Prologue": {
        "summary": "A low-ranking security trainee for the GelCap Guild (GG), secretly the illegitimate child of the CEO planted as a 'bloodline fallback', lives a monotonous life shadowed by their personal AI, G.R.A.C.E. A massive explosion destroys their facility, leaving them the sole survivor. Following 'GG' logos through the ruins, they discover a damaged time-travel pod ('GG Hype-'), which activates and hurls them into the past.",
        "major_events": [
            "Protagonist is established as an undervalued GelCap security trainee, secretly the CEO's illegitimate child.",
            "A massive explosion occurs during a lesson with G.R.A.C.E., leaving the protagonist unconscious in the ruined facility.",
            "Waking up as the sole survivor, the protagonist follows GG logos to a hidden, fire-scarred chamber.",
            "The protagonist discovers a 'shrink-class' transport pod that, when activated, becomes a Gel Capsule and initiates time travel."
        ]
    },
    "Act 1": {
        "summary": "The protagonist awakens in the Viking Age. They discover that the local warriors are unknowing ancestors of the GelCap Guild, using a primitive form of the corporation's signature purple gel in their helmets. To help the protagonist survive and blend in, G.R.A.C.E. sacrifices her core functions to provide a language translation module, going dormant as the protagonist approaches the Viking camp.",
        "major_events": [
            "The protagonist crash-lands in a forest clearing during the Viking Age.",
            "Observes Viking warriors wearing helmets padded with a purple gel G.R.A.C.E. identifies as a primitive form of GelCap substance.",
            "G.R.A.C.E. procures a helmet and clothes, then sacrifices all systems except for language translation to allow communication.",
            "With G.R.A.C.E. dormant but providing translation, the disguised protagonist walks toward the Viking settlement."
        ]
    },
    "Act 2": {
        "summary": "Forced into slave labor in the G\u00e6l Mines, the protagonist hones their physical abilities through grueling tasks. They craft a makeshift charger to partially awaken G.R.A.C.E., drawing the attention of the Guard Captain. Their training is interrupted by the arrival of the alien Pakariin, who eventually enslave the entire Viking camp. Guided by G.R.A.C.E.'s newly recovered memories of the Pakariin's ancient history, the protagonist learns of the legendary Frozen King. After defeating the brainwashed Valking Captain in a final confrontation, the protagonist earns their freedom and sets out to find the king, unlocking the path to Act 3.",
        "major_events": [
            "Protagonist is enslaved and sent to the G\u00e6l Mines to perform five core training tasks (Strength, Speed, Defense, Endurance, Focus).",
            "A 'Makeshift Charger' is crafted, partially reawakening G.R.A.C.E. to a whisper-mode.",
            "The alien Pakariin arrive, seeking the sealed Viking king.",
            "After the protagonist passes the 'Chasm Trial', the Pakariin return and conquer the camp, conscripting all survivors.",
            "G.R.A.C.E. reaches 50% power, revealing memories of the Pakariin's ancient presence and the legend of the Frozen King.",
            "Protagonist receives a cryptic vision from the Frozen King: 'Your presence is no longer ignored. The Captain watches. He prepares your reckoning.'",
            "The Guard Captain, now a brainwashed 'Valking Captain', is defeated in a boss battle, ending the Act."
        ]
    },
    "Act 3": {
        "summary": "Having defeated the Valking Captain, the protagonist is now a free Valking. Guided by G.R.A.C.E.'s recovered data, they begin their search for the Echo Chamber, a place tied to the Frozen King. This act follows the quest to awaken the only power known to have driven off the Pakariin in the past, setting the stage for a confrontation that will decide the fate of both the Viking past and the protagonist's destroyed future.",
        "major_events": [
            "The quest to find the Echo Chamber and awaken the Frozen King begins."
        ]
    }
}

# --- AI UPDATER FUNCTION ---

def run_ai_update(narrative_log):
    """Generates the updated Python code for the database."""
    data_string = f"PLAYER_STATE = {json.dumps(PLAYER_STATE, indent=4)}\n\nLORE_DATA = {json.dumps(LORE_DATA, indent=4)}"
    
    prompt = f"""You are a meticulous historian AI. Your task is to update the Python dictionaries containing the game's data based on a new narrative log.
NARRATIVE LOG: <log>{narrative_log}</log>
CURRENT GAME DATA: <code>{data_string}</code>
INSTRUCTIONS:
1. Read the new narrative log and the current game data.
2. Generate the complete, updated Python code for the `PLAYER_STATE` and `LORE_DATA` dictionaries.
3. Be exhaustive. Update stats, inventory, traits, companion statuses, and add historical events to the correct acts.
4. Your response should ONLY be the raw Python code for the two dictionaries. Do not include any other text, explanations, or markdown formatting. Start your response with `PLAYER_STATE = {{`"""
    try:
        # --- THIS IS THE FINAL, CORRECTED MODEL NAME ---
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"# An error occurred: {e}"

# --- UI DISPLAY FUNCTIONS ---
# (Unchanged)
def display_section(title, data):
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    with st.expander(f"**{item.get('name', 'Entry')}**"):
                        for k, v in item.items():
                            if k != 'name': st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.markdown(data)

def display_dict_section(title, data):
    if data:
        st.subheader(title)
        for key, value in data.items(): st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

# --- PAGE DEFINITIONS ---
# (Unchanged)
def render_character_sheet():
    st.title("Character Sheet")
    display_dict_section("🧍 Player Profile", PLAYER_STATE.get("profile"))
    st.subheader("📈 Stats Overview")
    cols = st.columns(3)
    i = 0
    for key, value in PLAYER_STATE.get("stats", {}).items():
        cols[i % 3].metric(label=key, value=value); i += 1
    traits = PLAYER_STATE.get("traits", {})
    st.subheader("🧬 Traits")
    display_section("Active", traits.get("active"))
    display_section("Echoform", traits.get("echoform"))
    display_section("Fused", traits.get("fused"))
    inventory = PLAYER_STATE.get("inventory", {})
    st.subheader("🎒 Inventory")
    display_section("Relics", inventory.get("relics"))
    display_section("Key Items", inventory.get("key_items"))
    display_dict_section("Equipment", inventory.get("equipment"))
    display_section("🧑‍🤝‍🧑 Companions", PLAYER_STATE.get("companions"))

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    lore_acts = list(LORE_DATA.keys())
    selected_act_title = st.sidebar.radio("View Lore Section:", lore_acts, key="lore_nav")
    act_data = LORE_DATA.get(selected_act_title, {})
    if act_data:
        display_section("📘 Summary", act_data.get("summary"))
        display_section("🧩 Major Events", act_data.get("major_events"))
    else:
        st.warning("No data found for this section.")

def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("The 'Play the Game' feature is under construction.")

# --- MAIN APP LAYOUT ---
st.sidebar.title("Navigation")
main_page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.markdown("---")
st.sidebar.title("🛠️ Lore Updater")
st.sidebar.subheader("Generate Updated Lore")
narrative_log_input = st.sidebar.text_area("Paste your new story information here:", height=200)

if st.sidebar.button("Generate Update Code"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY is not set in your .env file!")
    elif not narrative_log_input:
        st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("The AI is generating your updated lore code..."):
            updated_code = run_ai_update(narrative_log_input)
        
        st.sidebar.subheader("Updated Code:")
        st.sidebar.code(updated_code, language="python")
        st.sidebar.info("Copy the code above and paste it over the 'GAME DATABASE' section in this script to save the changes.")

if main_page == "Character Sheet":
    render_character_sheet()
elif main_page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()