class Resource:
    def __init__(self, ri, ra, rp, rw, rm, rl, ru, rt, re=0):
        self.id = ri
        self.activation_cost = ra
        self.maintenance_cost = rp
        self.active_turns = rw
        self.downtime = rm
        self.life_cycle = rl
        self.buildings_powered = ru
        self.type = rt
        self.effect = re
        self.remaining_life = rl
        self.is_active = False

    def activate(self):
        self.is_active = True

    def decrement_life(self):
        if self.remaining_life > 0:
            self.remaining_life -= 1

    def is_expired(self):
        return self.remaining_life <= 0

class Turn:
    def __init__(self, tm, tx, tr):
        self.min_buildings = tm
        self.max_buildings = tx
        self.profit_per_building = tr

class GreenRevolutionGame:
    def __init__(self, initial_budget, resources, turns):
        self.budget = initial_budget
        self.resources = {r.id: r for r in resources}
        self.turns = turns
        self.owned_resources = []
        self.purchase_log = []

    def purchase_resource(self, resource_id, turn_number):
        resource = self.resources[resource_id]
        if self.budget >= resource.activation_cost:
            self.budget -= resource.activation_cost
            self.owned_resources.append(resource)
            resource.activate()
            self.purchase_log.append((turn_number, resource_id))

    def simulate_game(self):
        for turn_number, turn in enumerate(self.turns):
            powered_buildings = sum(r.buildings_powered for r in self.owned_resources if r.is_active)
            powered_buildings = min(powered_buildings, turn.max_buildings)
            
            if powered_buildings >= turn.min_buildings:
                profit = powered_buildings * turn.profit_per_building
            else:
                profit = 0
            
            maintenance_costs = sum(r.maintenance_cost for r in self.owned_resources if r.is_active)
            self.budget += profit - maintenance_costs
            
            for resource in self.owned_resources:
                resource.decrement_life()
                if resource.is_expired():
                    self.owned_resources.remove(resource)
            
            # Example purchase strategy: Buy the cheapest resource that fits in the budget
            affordable_resources = [r for r in self.resources.values() if r.activation_cost <= self.budget]
            if affordable_resources:
                best_choice = min(affordable_resources, key=lambda r: r.activation_cost)
                self.purchase_resource(best_choice.id, turn_number)

        return self.generate_output()

    def generate_output(self):
        output = []
        purchases_by_turn = {}
        for turn, rid in self.purchase_log:
            if turn not in purchases_by_turn:
                purchases_by_turn[turn] = []
            purchases_by_turn[turn].append(rid)
        
        for turn in sorted(purchases_by_turn.keys()):
            output.append(f"{turn} {len(purchases_by_turn[turn])} " + " ".join(map(str, purchases_by_turn[turn])))
        
        return "\n".join(output)

# Example usage with given input:
initial_budget = 10
resources = [
    Resource(1, 16, 3, 1, 1, 3, 6, 'D', 2),
    Resource(2, 2, 2, 1, 3, 5, 4, 'X'),
    Resource(3, 14, 15, 2, 2, 5, 3, 'C', 1),
    Resource(4, 20, 9, 2, 1, 3, 4, 'E', 3),
    Resource(5, 10, 8, 2, 1, 3, 3, 'X')
]
turns = [
    Turn(3, 5, 4),
    Turn(5, 6, 3),
    Turn(2, 7, 4),
    Turn(4, 6, 3),
    Turn(4, 7, 1),
    Turn(5, 7, 4)
]

game = GreenRevolutionGame(initial_budget, resources, turns)
print(game.simulate_game())