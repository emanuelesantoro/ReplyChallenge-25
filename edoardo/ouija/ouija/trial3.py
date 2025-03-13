import sys
import random
from collections import deque
from itertools import combinations
from tqdm import tqdm

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
        self.effect_value = effect_value
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
    def __init__(self, initial_budget, resources, turns, num_samples=10):
        self.budget = initial_budget
        self.resources = {r.id: r for r in resources}
        self.turns = turns
        self.active_resources = []
        self.accumulator = 0
        self.game_log = []
        self.num_samples = num_samples  # Number of sampled selections per turn

    def apply_special_effects(self, resource):
        """Applies special effects of a resource properly."""
        if resource.special_effect == 'A':  # Increase powered buildings
            for r in self.active_resources:
                r.buildings_powered += int(r.buildings_powered * resource.effect_value / 100)

        elif resource.special_effect == 'B':  # Adjust TM and TX
            for turn in self.turns:
                turn.min_buildings += int(turn.min_buildings * resource.effect_value / 100)
                turn.max_buildings += int(turn.max_buildings * resource.effect_value / 100)

        elif resource.special_effect == 'C':  # Increase lifecycle
            for r in self.active_resources:
                r.lifecycle += int(r.lifecycle * resource.effect_value / 100)

        elif resource.special_effect == 'D':  # Increase profit per building
            for turn in self.turns:
                turn.profit_per_building += int(turn.profit_per_building * resource.effect_value / 100)

        elif resource.special_effect == 'E':  # Accumulator
            self.accumulator += resource.effect_value



    def generate_candidate_selections(self, available_resources):
        """Generate multiple random valid selections of resources to explore different solutions."""
        sampled_selections = []
        for _ in tqdm(range(self.num_samples)):
            num_selected = random.randint(1, min(len(available_resources), 5))  # Select up to 5 at random
            sampled_selection = random.sample(available_resources, num_selected)
            sampled_selections.append(sampled_selection)
        return sampled_selections

    def evaluate_selection(self, selected_resources, turn):
        """Evaluate a selection of resources based on profit and budget constraints."""
        total_buildings = sum(r.buildings_powered for r in selected_resources)
        activation_cost = sum(r.activation_cost for r in selected_resources)
        periodic_cost = sum(r.periodic_cost for r in selected_resources)

        # Profit calculation
        if total_buildings >= turn.min_buildings:
            profit = min(total_buildings, turn.max_buildings) * turn.profit_per_building
        else:
            profit = 0
        
        net_profit = profit - periodic_cost
        return net_profit, activation_cost, selected_resources

            
    def force_minimum_power(self, available_resources, min_buildings):
        """Forces selection of resources to meet at least TM buildings."""
        # Filter out inactive resources (must be active this turn)
        available_resources = [r for r in available_resources if r.buildings_powered > 0 and r.is_active()]
        
        # Sort by cost-effectiveness (avoid division by zero)
        available_resources.sort(key=lambda r: (r.activation_cost / r.buildings_powered) if r.buildings_powered > 0 else float('inf'))
        
        selection = []
        total_powered = 0
        total_cost = 0

        for resource in available_resources:
            if total_powered >= min_buildings:
                break  # Stop once we reach TM

            if total_cost + resource.activation_cost <= self.budget:
                selection.append(resource)
                total_powered += resource.buildings_powered
                total_cost += resource.activation_cost

        # If still not enough buildings, return empty (meaning failure)
        return selection if total_powered >= min_buildings else []


    def select_best_resources(self, turn_index):
        """Selects resources ensuring at least TM buildings are powered."""
        turn = self.turns[turn_index]
        available_resources = [r for r in self.resources.values() if r.activation_cost <= self.budget and r.is_active()]

        if not available_resources:
            return []

        best_selection = []
        best_profit = float('-inf')

        for selection in self.generate_candidate_selections(available_resources):
            total_buildings = sum(r.buildings_powered for r in selection)

            # Ensure the selection meets at least TM buildings
            if total_buildings < turn.min_buildings:
                continue  # Skip selections that fail to power enough buildings

            profit, cost, resources = self.evaluate_selection(selection, turn)

            # Ensure selection is within budget and maximizes profit
            if cost <= self.budget and profit > best_profit:
                best_profit = profit
                best_selection = resources

        # If no selection met TM, force-buy resources
        if not best_selection:
            best_selection = self.force_minimum_power(available_resources, turn.min_buildings)

        return best_selection




    def purchase_resources(self, turn_index):
        best_resources = self.select_best_resources(turn_index)
        purchased = []

        for resource in best_resources:
            if self.budget >= resource.activation_cost:
                self.budget -= resource.activation_cost
                self.active_resources.append(resource)
                purchased.append(resource.id)
                self.apply_special_effects(resource)

        if purchased:
            self.game_log.append(f"{turn_index} {len(purchased)} " + " ".join(map(str, purchased)))
        print(f"Turn {turn_index}: Purchased resources {purchased}")

    def play_game(self):
        for turn_index, turn in enumerate(self.turns):
            print(f"Turn {turn_index} - BUDGET: {self.budget}")
            self.purchase_resources(turn_index)

            # Calculate total powered buildings
            total_powered_buildings = sum(r.buildings_powered for r in self.active_resources if r.is_active())

            # Force-buy extra resources if powered buildings are below TM
            if total_powered_buildings < turn.min_buildings:
                needed = turn.min_buildings - total_powered_buildings

                # Use accumulator if available
                if self.accumulator > 0:
                    used_from_accumulator = min(self.accumulator, needed)
                    total_powered_buildings += used_from_accumulator
                    self.accumulator -= used_from_accumulator

                # If accumulator is not enough, buy extra resources
                if total_powered_buildings < turn.min_buildings:
                    print(f"⚠️ ERROR: Not enough buildings powered! Needed: {turn.min_buildings}, Got: {total_powered_buildings}")
                    
                    additional_resources = self.force_minimum_power(
                        [r for r in self.resources.values() if r.activation_cost <= self.budget], turn.min_buildings
                    )

                    # If we still can't meet TM, print an error and skip the turn
                    if not additional_resources:
                        print(f"❌ CRITICAL: Could not power enough buildings. Skipping turn {turn_index}.")
                        continue

                    # Add these resources to active resources
                    for r in additional_resources:
                        self.budget -= r.activation_cost
                        self.active_resources.append(r)
                        print(f"✅ Buying extra resource {r.id} to meet TM.")

                    # Recalculate powered buildings
                    total_powered_buildings = sum(r.buildings_powered for r in self.active_resources if r.is_active())

            # Ensure powered buildings are within TM and TX
            total_powered_buildings = min(max(total_powered_buildings, turn.min_buildings), turn.max_buildings)
            profit = total_powered_buildings * turn.profit_per_building

            print(f"TURN {turn_index}: Buildings Powered = {total_powered_buildings}, Profit = {profit}")

            # Compute periodic maintenance cost
            maintenance_cost = sum(r.periodic_cost for r in self.active_resources if r.is_active())

            # Update budget
            net_change = profit - maintenance_cost
            if self.budget + net_change < 0:
                print("WARNING: Budget would go negative. Adjusting to zero.")
                self.budget = 0
            else:
                self.budget += net_change

            # Update lifecycle of active resources
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

    game = GreenRevolutionGame(D, resource_list, turn_list, num_samples=200000)  # More samples for better optimization
    results = game.play_game()

    with open(output_file, 'w') as f:
        f.write("\n".join(results))
