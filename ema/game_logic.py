
class Resource:
    current_active_turns = 0
    current_maintenance_turns = 0
    remaining_lyfecycles = 0
    # not in maintenance
    active = False
    # permanently dead
    dead = False
    game = None
    def __init__(self, game, **kwargs):
        self.game = game
        self.resource_id = kwargs["Resource ID"]
        self.activation_cost = kwargs["Activation Cost"]
        self.periodic_cost = kwargs["Periodic Cost"]
        self.active_turns = kwargs["Active Turns"]
        self.downtime_turns = kwargs["Downtime Turns"]
        self.life_cycle = kwargs["Life Cycle"]
        self.buildings_powered = kwargs["Buildings Powered"]
        self.special_effect = kwargs["Special Effect"]
        self.efficiency_rating = kwargs["Efficiency Rating"]

        self.current_active_turns = self.active_turns
        self.remaining_lyfecycles = self.life_cycle
    def update(self):
        if self.current_active_turns > 0:
            self.current_active_turns -= 1
            if self.current_active_turns == 0 and self.active:
                self.active = False
                self.current_maintenance_turns = self.downtime_turns
        elif self.current_maintenance_turns > 0:
            self.current_maintenance_turns -= 1
            if self.current_maintenance_turns == 0 and not self.active:
                if self.remaining_lyfecycles > 0:
                    self.active = True
                    self.current_active_turns = self.active_turns
                    self.remaining_lyfecycles -= 1
                else:
                    self.dead = True

def calculate_new_buildings_powered(resource, game):
    base_power = resource.buildings_powered
    total_additional_effect = 0

    # Iterate through all active resources in the game
    for active_resource in game.current_resources:
        # If the resource is of type A and is active, add its efficiency rating to the total effect
        if active_resource["Special Effect"] == "A" and active_resource.active:
            total_additional_effect += active_resource.efficiency_rating
    
    # Calculate the new buildings powered value by adding the total effect from active A resources
    if total_additional_effect > 0:
        new_buildings_powered = base_power * (1 + total_additional_effect / 100)
    else:
        new_buildings_powered = base_power * (1 - abs(total_additional_effect) / 100)

    # Floor the final value to an integer as per the rule
    return int(new_buildings_powered)

def calculate_new_thresholds(current_turn, game):
    # Get the current turn's thresholds (TM and TX) from the game state
    tm = current_turn["Minimum Buildings"]
    tx = current_turn["Maximum Buildings"]
    
    total_additional_effect = 0  # To accumulate the effects of active B-type resources
    
    # Apply the effect of each active Resource B on the thresholds
    for active_resource in game.current_resources:
        if active_resource["Special Effect"] == "B" and active_resource.active:
            efficiency = active_resource.efficiency_rating
            total_additional_effect += efficiency  # Add the efficiency of active B resources
            
    # Apply the accumulated effect to the thresholds
    if total_additional_effect > 0:
        # Green Resource (increase thresholds)
        tm = int(tm * (1 + total_additional_effect / 100))  # Increase minimum threshold by percentage
        tx = int(tx * (1 + total_additional_effect / 100))  # Increase maximum threshold by percentage
    else:
        # Non-Green Resource (decrease thresholds)
        tm = int(tm * (1 - abs(total_additional_effect) / 100))  # Decrease minimum threshold by percentage
        tx = int(tx * (1 - abs(total_additional_effect) / 100))  # Decrease maximum threshold by percentage

    # Ensure that TM and TX do not go below 0
    tm = max(0, tm)
    tx = max(0, tx)
    
    return tm, tx
def calculate_new_profit(current_turn, game):
    profit = current_turn["Profit"]
    # Calculate the new profit of the current turn based on the effects of active resources of type D
    total_additional_effect = 0
    for active_resource in game.current_resources:
        if active_resource["Special Effect"] == "D" and active_resource.active:
            total_additional_effect += active_resource.efficiency_rating
    if total_additional_effect > 0:
        profit = profit * (1 + total_additional_effect / 100)
    else:
        profit = profit * (1 - abs(total_additional_effect) / 100)
    return profit
class Game:
    def __init__(self, D, R, T, resources, turns):
        self.D = D
        self.R = R
        self.T = T
        self.available_resources = [Resource(self, **resource) for resource in resources]
        self.turns = turns
        self.current_turn_id = 0
        self.current_budget = D
        self.current_resources = []
    
    def get_currently_active_buildings(self):
        total_buildings_powered = 0

        # For each active resource, calculate the updated buildings powered based on active "A" resources
        for resource in self.current_resources:
            if resource.active:
                # Apply the effect of any active "A" resources to this resource's buildings powered
                updated_buildings_powered = calculate_new_buildings_powered(resource, self)
                total_buildings_powered += updated_buildings_powered
        
        return total_buildings_powered

    def perform_turn(self, bought_resources_list: list):
        # periodic costs
        for resource in self.current_resources:
            if resource.dead:
                self.current_resources.remove(resource)
                continue
            self.current_budget -= resource.periodic_cost

        # update resources + activation costs
        for resource in bought_resources_list:
            self.current_budget -= resource.activation_cost
            resource.active = True
            resource.current_active_turns = resource.active_turns
            self.current_resources.append(resource)
        
        # add profits
        current_turn = self.turns[self.current_turn_id]
        # Calculate the new thresholds based on the current turn and the game state
        max_buildings, min_buildings = calculate_new_thresholds(current_turn, self)
        profit = calculate_new_profit(current_turn, self)
        if self.get_currently_active_buildings() >= min_buildings:
            self.current_budget += profit * min(max_buildings, self.get_currently_active_buildings())
        
        for resource in self.current_resources:
            resource.update()
        
        self.current_turn_id += 1