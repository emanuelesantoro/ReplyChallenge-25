import sys
from collections import deque

class Resource:
    def __init__(self, resource_id, activation_cost, periodic_cost, active_turns, downtime_turns, lifecycle, buildings_powered, special_effect, effect_value=None):
        self.id = resource_id
        self.activation_cost = activation_cost
        self.periodic_cost = periodic_cost
        self.active_turns = active_turns
        self.downtime_turns = downtime_turns
        self.lifecycle = lifecycle
        self.buildings_powered = buildings_powered
        self.special_effect = special_effect
        self.effect_value = effect_value  # Percentage effect or accumulator capacity
        self.remaining_lifetime = lifecycle
        self.active_state = deque([1] * active_turns + [0] * downtime_turns, maxlen=lifecycle)
    
    def update_lifecycle(self):
        if self.remaining_lifetime > 0:
            self.remaining_lifetime -= 1
            self.active_state.rotate(-1)
    
    def is_active(self):
        return self.remaining_lifetime > 0 and self.active_state[0] == 1

class Turn:
    def __init__(self, min_buildings, max_buildings, profit_per_building):
        self.min_buildings = min_buildings
        self.max_buildings = max_buildings
        self.profit_per_building = profit_per_building

class GreenRevolutionGame:
    def __init__(self, initial_budget, resources, turns):
        self.budget = initial_budget
        self.resources = {r.id: r for r in resources}
        self.turns = turns
        self.active_resources = []
        self.accumulator = 0
        self.game_log = []
    
    def apply_special_effects(self):
        for resource in self.active_resources:
            if resource.is_active():
                if resource.special_effect == 'A':  # Smart Meter
                    for r in self.active_resources:
                        r.buildings_powered = max(0, r.buildings_powered + int(r.buildings_powered * resource.effect_value / 100))
                elif resource.special_effect == 'B':  # Distribution Facility
                    for turn in self.turns:
                        turn.min_buildings = max(0, turn.min_buildings + int(turn.min_buildings * resource.effect_value / 100))
                        turn.max_buildings = max(turn.min_buildings + 1, turn.max_buildings + int(turn.max_buildings * resource.effect_value / 100))
                elif resource.special_effect == 'C':  # Maintenance Plan
                    for r in self.active_resources:
                        r.lifecycle = max(1, r.lifecycle + int(r.lifecycle * resource.effect_value / 100))
                elif resource.special_effect == 'D':  # Renewable Plant
                    for turn in self.turns:
                        turn.profit_per_building = max(0, turn.profit_per_building + int(turn.profit_per_building * resource.effect_value / 100))
                elif resource.special_effect == 'E':  # Accumulator
                    self.accumulator += resource.effect_value
    
    def purchase_resources(self, turn_index):
        affordable_resources = sorted(self.resources.values(), key=lambda r: r.activation_cost)
        purchased = []
        while affordable_resources and self.budget >= affordable_resources[0].activation_cost:
            resource = affordable_resources.pop(0)
            self.budget -= resource.activation_cost
            self.active_resources.append(resource)
            purchased.append(resource.id)
        if purchased:
            self.game_log.append(f"{turn_index} {len(purchased)} " + " ".join(map(str, purchased)))
    
    def play_game(self):
        for turn_index, turn in enumerate(self.turns):
            self.purchase_resources(turn_index)
            self.apply_special_effects()
            total_powered_buildings = sum(r.buildings_powered for r in self.active_resources if r.is_active())
            if total_powered_buildings < turn.min_buildings and self.accumulator > 0:
                needed = turn.min_buildings - total_powered_buildings
                used_from_accumulator = min(self.accumulator, needed)
                total_powered_buildings += used_from_accumulator
                self.accumulator -= used_from_accumulator
            if total_powered_buildings >= turn.min_buildings:
                profit = min(total_powered_buildings, turn.max_buildings) * turn.profit_per_building
            else:
                profit = 0
            maintenance_cost = sum(r.periodic_cost for r in self.active_resources if r.is_active())
            self.budget += profit - maintenance_cost
            for resource in self.active_resources:
                resource.update_lifecycle()
        return self.game_log

if __name__ == "__main__":
    input_file = "../1-thunberg.txt"
    output_file = "../out.txt"
    
    with open(input_file, 'r') as f:
        lines = f.read().splitlines()
    
    D, R, T = map(int, lines[0].split())
    resource_list = []
    turn_list = []
    
    for i in range(1, R + 1):
        parts = lines[i].split()
        resource_id, activation_cost, periodic_cost, active_turns, downtime_turns, lifecycle, buildings_powered = map(int, parts[:7])
        special_effect = parts[7]
        effect_value = int(parts[8]) if len(parts) > 8 else None
        resource_list.append(Resource(resource_id, activation_cost, periodic_cost, active_turns, downtime_turns, lifecycle, buildings_powered, special_effect, effect_value))
    
    for i in range(R + 1, R + T + 1):
        min_buildings, max_buildings, profit_per_building = map(int, lines[i].split())
        turn_list.append(Turn(min_buildings, max_buildings, profit_per_building))
    
    game = GreenRevolutionGame(D, resource_list, turn_list)
    results = game.play_game()
    
    with open(output_file, 'w') as f:
        f.write("\n".join(results))