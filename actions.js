// actions.js

export const tasks = {
  cart: {
    name: "Push Ore Cart",
    sillCost: 5,
    duration: 3,
    stat: "Strength"
  },
  rock: {
    name: "Break Rocks",
    sillCost: 8,
    duration: 4,
    stat: "Defense"
  },
  tunnel: {
    name: "Dig Tunnel",
    sillCost: 10,
    duration: 6,
    stat: "Endurance"
  },
  shift: {
    name: "End Shift",
    sillCost: 4,
    duration: 2,
    stat: "Focus"
  },
  focus: {
    name: "Mindful Mining",
    sillCost: 6,
    duration: 5,
    stat: "Focus"
  }
};

export const monsters = {
  boar: {
    name: "Wild Boar",
    sillCost: 10,
    duration: 4,
    reward: { stat: "Attack", gel: 5 }
  },
  elk: {
    name: "Mountain Elk",
    sillCost: 12,
    duration: 6,
    reward: { stat: "Endurance", gel: 8 }
  },
  wolf: {
    name: "Lone Wolf",
    sillCost: 14,
    duration: 7,
    reward: { stat: "Defense", gel: 10 }
  },
  lynx: {
    name: "Silent Lynx",
    sillCost: 16,
    duration: 8,
    reward: { stat: "Focus", gel: 12 }
  },
  bear: {
    name: "Giant Bear",
    sillCost: 20,
    duration: 10,
    reward: { stat: "Attack", gel: 15 }
  }
};
