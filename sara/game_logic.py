
class Resource:

    current_active_turns = 0
    current_maintenance_turns = 0
    remaining_lyfecycles = 0
    # not in maintenance
    active = False
    # permanently dead
    dead = False
    
    def __init__(self, **kwargs):
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


class Game:

    def __init__(self, D, R, T, resources, turns):
        self.D = D
        self.R = R
        self.T = T
        self.available_resources = [Resource(**resource) for resource in resources]
        self.turns = turns
        self.current_turn_id = 0
        self.current_budget = D
        self.current_resources = []
    
    def get_currently_active_buildings(self):
        return sum(resource.buildings_powered for resource in self.resources if resource.active)
    
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
        max_buildings = current_turn["Maximum Buildings"]
        min_buildings = current_turn["Minimum Buildings"]
        profit = current_turn["Profit"]
        if self.get_currently_active_buildings() >= min_buildings:
            self.current_budget += profit * min(max_buildings, self.get_currently_active_buildings())
        
        for resource in self.current_resources:
            resource.update()
        
        self.current_turn_id += 1