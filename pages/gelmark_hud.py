
import streamlit as st
import json
from typing import List, Dict

st.set_page_config(layout="wide")

# --- TRAITS ---
class Trait:
    def __init__(self, name: str, type_: str, description: str):
        self.name = name
        self.type = type_
        self.description = description

    def __repr__(self):
        return f"{self.name} ({self.type})"

# --- COMPANIONS ---
class Companion:
    def __init__(self, name: str):
        self.name = name
        self.sync_rate = 0
        self.traits: List[Trait] = []

    def add_trait(self, trait: Trait):
        self.traits.append(trait)

    def get_bonuses(self):
        return [f"{trait.name}: {trait.description}" for trait in self.traits]

# --- TRAIT REGISTRY ---
TRAIT_REGISTRY = {
    "Commandless Grace": Trait("Commandless Grace", "Permanent", "An origin-bound resilience from a fractured future."),
    "Blessing of Askr": Trait("Blessing of Askr", "Permanent", "A relic-born boon tied to the world roots."),
    "Grace of the Verdant Fracture": Trait("Grace of the Verdant Fracture", "Hybrid", "A synthesis of Grace and Askr, echo-bound."),
    "Echo Resilience": Trait("Echo Resilience", "Echoform", "Boosts vision clarity when sync exceeds 50% with AI companions."),
}

FUSION_MAP = {
    ("Commandless Grace", "Blessing of Askr"): {
        "result": TRAIT_REGISTRY["Grace of the Verdant Fracture"],
        "shrine": "Memoryfire Crucible",
        "companion_sync": {"G.R.A.C.E.": 25}
    },
}

# --- PLAYER ---
class Player:
    def __init__(self):
        self.arc_rank = "Pulsebearer"
        self.traits: List[Trait] = []
        self.inventory: List[str] = []
        self.shrine_history: List[str] = []
        self.visions: List[str] = []
        self.companions: Dict[str, Companion] = {}

    def add_trait(self, trait: Trait):
        self.traits.append(trait)

    def has_trait(self, trait_name: str):
        return any(t.name == trait_name for t in self.traits)

    def fuse_traits(self, t1: str, t2: str):
        key = (t1, t2) if (t1, t2) in FUSION_MAP else (t2, t1)
        if key in FUSION_MAP:
            info = FUSION_MAP[key]
            if info['shrine'] not in self.shrine_history:
                return f"Visit required shrine: {info['shrine']}"
            for comp, req in info.get('companion_sync', {}).items():
                if self.companions.get(comp, Companion(comp)).sync_rate < req:
                    return f"Sync with {comp} must be at least {req}"
            if self.has_trait(t1) and self.has_trait(t2):
                self.traits = [t for t in self.traits if t.name not in key]
                self.add_trait(info['result'])
                return f"Fused {t1} and {t2} into {info['result'].name}"
            return "Required traits not found."
        return "Invalid trait combination."

    def update_sync(self, name: str, delta: int):
        if name in self.companions:
            self.companions[name].sync_rate = min(100, max(0, self.companions[name].sync_rate + delta))

    def log_shrine_visit(self, name: str):
        self.shrine_history.append(name)

    def log_vision(self, vision: str):
        self.visions.append(vision)

    def display(self):
        st.title("Gelmark HUD")
        st.subheader(f"Arc Rank: {self.arc_rank}")
        st.write("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Traits")
            for t in self.traits:
                st.markdown(f"**{t.name}** *({t.type})* — {t.description}")

        with col2:
            st.subheader("Inventory")
            for item in self.inventory:
                st.markdown(f"- {item}")

        with col3:
            st.subheader("Shrines Visited")
            for shrine in self.shrine_history:
                st.markdown(f"- {shrine}")

        st.write("---")
        st.subheader("Companions")
        for cname, comp in self.companions.items():
            st.markdown(f"**{cname}** – Sync: {comp.sync_rate}%")
            for bonus in comp.get_bonuses():
                st.markdown(f"➤ {bonus}")

        st.write("---")
        st.subheader("Visions")
        for v in self.visions:
            st.markdown(f"🔮 {v}")

        st.write("---")
        st.subheader("Fusion Interface")
        tnames = [t.name for t in self.traits]
        if len(tnames) >= 2:
            t1 = st.selectbox("First Trait", tnames)
            t2 = st.selectbox("Second Trait", [t for t in tnames if t != t1])
            if st.button("Fuse Traits"):
                st.success(self.fuse_traits(t1, t2))

        st.write("---")
        st.subheader("Seer's Pulse — Rank Choices")
        choices = st.text_area("Enter narrative choices (one per line):").split("\n")

        def score_choice(choice: str) -> int:
            keywords = ["honor", "sacrifice", "resolve", "echo", "fracture", "pulse"]
            return sum(3 for word in keywords if word in choice.lower()) + len(choice)

        ranked = sorted([(c, score_choice(c)) for c in choices if c.strip()], key=lambda x: -x[1])
        for i, (text, score) in enumerate(ranked):
            st.markdown(f"**{i+1}.** {text} *(score: {score})*")

        if ranked:
            top = ranked[0][0]
            self.log_vision(f"Seer’s Pulse ranked top: {top}")

def main():
    player = Player()
    player.add_trait(TRAIT_REGISTRY["Commandless Grace"])
    player.add_trait(TRAIT_REGISTRY["Blessing of Askr"])
    player.inventory.append("Coreborn Hammer")
    player.log_shrine_visit("Memoryfire Crucible")
    player.log_vision("Vision Tier 2: Echoed Past")
    player.companions["G.R.A.C.E."] = Companion("G.R.A.C.E.")
    player.companions["G.R.A.C.E."].add_trait(TRAIT_REGISTRY["Echo Resilience"])
    player.update_sync("G.R.A.C.E.", 30)
    player.display()

if __name__ == "__main__":
    main()
