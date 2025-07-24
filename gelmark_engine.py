# This is the Gelmark Engine: a single, self-contained application.

import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the secret key from the .env file at the start
load_dotenv()

# --- Configuration ---
st.set_page_config(page_title="Gelmark Engine", layout="wide")


# --- GAME DATABASE (All your lore and stats are now stored here directly) ---

PLAYER_STATE = {
    "profile": {
        "name_title": "Askr, Pulse-Bearer of the Fractured Oath",
        "current_arc_act": "Act 3, Chapter 4: The Sightless Hollow",
        "origin_class_lineage": "Human, Time-Sent Heir of GelCap, Echo-Kin Hybrid (Threadcaller / Memorykeeper)",
        "covenant_oath": "Vow to become a sanctuary for the unremembered."
    },
    "stats": {
        "Strength": 13, "Dexterity": 10, "Insight": 10,
        "Focus": 12, "Charisma": 1, "Resolve": 10,
        "Spirit": 10, "Agility": 10, "Willpower": 10, "Lore": 10
    },
    "traits": {
        "active": ["Oathbraid", "Commandless Grace"],
        "echoform": ["Mirrorburst"],
        "fused": ["Twin Flame Anchor", "Scorchbind Core", "Pulse Woven"]
    },
    "inventory": {
        "relics": [{"name": "Witness Unchosen", "effect": "Resists recursion threats."}],
        "key_items": ["Fragmented Keystone"],
        "equipment": {
            "weapon": "Coreborn Hammer (Inert)",
            "armor": "Memorybound Cloak"
        }
    },
    "companions": [
        {
            "name": "G.R.A.C.E.",
            "sync": "115%",
            "status": "Deeply bonded, Override Dialogue unlocked."
        },
        {
            "name": "Thjolda",
            "sync": "100%",
            "status": "Bond maxed after 'The Blade Before the Call' trial."
        },
        {
            "name": "Caelik",
            "sync": "100%",
            "status": "Bond maxed after 'Ash Born Twice' trial."
        }
    ]
}

LORE_DATA = {
    "Prologue": {
        "summary": "A low-ranking GelCap Guild security trainee, secretly the illegitimate child of the CEO, survives a devastating explosion. Guided by his AI, G.R.A.C.E., he discovers a time-traveling Gel Capsule and is propelled into the ancient past.",
        "major_events": [
            "The protagonist is established as a 'bloodline fallback' for the GelCap CEO.",
            "A facility-wide explosion kills everyone except the protagonist.",
            "A time-traveling Gel Capsule is discovered and activated."
        ],
    },
    "Act 1": {
        "summary": "Stranded in a Viking Age, the protagonist must adapt to survive. G.R.A.C.E. sacrifices most of her functionality to enable language translation, and the protagonist steps into the origin of the GelCap Guild itself.",
        "major_events": [
            "The protagonist lands in a cold, forested Viking Age.",
            "Observes warriors using a primitive form of GelCap material in their helmets.",
            "G.R.A.C.E. shuts down all systems but speech translation.",
            "The protagonist, disguised, walks toward the Viking camp."
        ],
    },
    "Act 2": {
        "summary": "Enslaved by the Vikings, the protagonist endures grueling labor in the Gæl Mines, which serves as a training ground. They grow in power, partially reawaken G.R.A.C.E., and face the arrival of a new alien threat, the Pakariin, before becoming a Valking and setting out to awaken the Frozen King.",
        "major_events": [
            "Enslaved and sent to the Gæl Mines.",
            "Core stats (Strength, Speed, etc.) are trained through mining tasks.",
            "A makeshift charger partially revives G.R.A.C.E.",
            "The alien Pakariin arrive and conscript the camp.",
            "The protagonist joins the Valking order and begins the quest to awaken the Frozen King."
        ],
    },
    "Act 3": {
        "summary": "Askr's journey through the remnants of the Dominion's influence, exploring shattered vaults and forging deeper bonds. The act culminates in the acquisition of the Temporal Flame Relic and the unfolding of a complex mystery involving Grace’s origins and the true nature of the Echo Keys.",
        "major_events": [
            "Dominion Vault Cleared.",
            "Vault Key 2 (Dominion Echo Anchor) acquired.",
            "Strength + Speed Echoform Trials completed.",
            "Flamebound Echo (Thjolda) quest completed.",
            "Dominion Warden defeated.",
            "Arcflare triggered."
        ]
    }
}


# --- UI DISPLAY FUNCTIONS ---

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
        # You can add more display sections here as needed
    else:
        st.warning("No data found for this section.")

def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("The 'Play the Game' feature is under construction. Future versions will allow you to continue your story directly from here.")
    # Placeholder for chat functionality

# --- MAIN APP LAYOUT ---
st.sidebar.title("Navigation")
main_page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.markdown("---")

# Updater tool is removed for simplicity, as all data is now hardcoded.
# Future versions could re-introduce an AI updater.

if main_page == "Character Sheet":
    render_character_sheet()
elif main_page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()