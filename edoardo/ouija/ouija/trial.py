import math
from collections import defaultdict

def parse_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Read initial game parameters
    D, R, T = map(int, lines[0].split())
    
    # Read resources
    resources = []
    for i in range(1, R + 1):
        data = lines[i].split()
        resource = {
            "RI": int(data[0]), "RA": int(data[1]), "RP": int(data[2]), "RW": int(data[3]),
            "RM": int(data[4]), "RL": int(data[5]), "RU": int(data[6]), "RT": data[7],
            "RE": int(data[8]) if len(data) > 8 else None  # Some resources may not have RE
        }
        resources.append(resource)
    
    # Read turns
    turns = []
    for i in range(R + 1, R + 1 + T):
        TM, TX, TR = map(int, lines[i].split())
        turns.append({"TM": TM, "TX": TX, "TR": TR})
    
    return D, R, T, resources, turns

class Resource:
    def __init__(self, resource_id, resource_type, activation_cost, periodic_cost, ru, rl, re, lifespan):
        self.id = resource_id
        self.type = resource_type
        self.activation_cost = activation_cost  # Initial cost
        self.periodic_cost = periodic_cost  # Recurring cost per turn
        self.ru = ru  # Buildings powered
        self.rl = rl  # Resource lifespan (turns active)
        self.re = re  # Impact percentage
        self.remaining_life = lifespan  # Remaining turns active
        self.is_active = True
    
    def apply_effect(self, game):
        """Applies special effects depending on the resource type."""
        if self.type == 'A':
            for res in game.active_resources:
                if res.is_active:
                    if self.re > 0:
                        res.ru += math.floor(res.ru * (self.re / 100))
                    else:
                        res.ru = max(0, res.ru + math.floor(res.ru * (self.re / 100)))
        elif self.type == 'B':
            if self.re > 0:
                game.tm += math.floor(game.tm * (self.re / 100))
                game.tx += math.floor(game.tx * (self.re / 100))
            else:
                game.tm = max(0, game.tm + math.floor(game.tm * (self.re / 100)))
                game.tx = max(0, game.tx + math.floor(game.tx * (self.re / 100)))
        elif self.type == 'C':
            for res in game.purchased_this_turn:
                if self.re > 0:
                    res.remaining_life += math.floor(res.remaining_life * (self.re / 100))
                else:
                    res.remaining_life = max(1, res.remaining_life + math.floor(res.remaining_life * (self.re / 100)))
        elif self.type == 'D':
            if self.re > 0:
                game.tr += math.floor(game.tr * (self.re / 100))
            else:
                game.tr = max(0, game.tr + math.floor(game.tr * (self.re / 100)))
        elif self.type == 'E':
            game.has_accumulator = True

class GameSimulator:
    def __init__(self, initial_budget, tm, tx, tr):
        self.budget = initial_budget
        self.tm = tm  # Minimum buildings needed for profit
        self.tx = tx  # Maximum buildings that can be powered
        self.tr = tr  # Profit per building
        self.active_resources = []
        self.purchased_this_turn = []
        self.has_accumulator = False
        self.accumulator_storage = 0

    def purchase_resource(self, resource):
        if self.budget >= resource.activation_cost:
            self.budget -= resource.activation_cost
            self.active_resources.append(resource)
            self.purchased_this_turn.append(resource)
            resource.apply_effect(self)
        
    def simulate_turn(self):
        # Pay maintenance costs
        total_cost = sum(res.periodic_cost for res in self.active_resources if res.is_active)
        if self.budget < total_cost:
            return "Game Over - Not enough funds."
        
        self.budget -= total_cost
        
        # Calculate buildings powered
        total_powered = sum(res.ru for res in self.active_resources if res.is_active)
        if self.has_accumulator and total_powered > self.tx:
            self.accumulator_storage += (total_powered - self.tx)
        if self.has_accumulator and total_powered < self.tm and self.accumulator_storage > 0:
            needed = self.tm - total_powered
            draw = min(needed, self.accumulator_storage)
            total_powered += draw
            self.accumulator_storage -= draw
        
        # Compute profit
        profit = self.tr * total_powered if total_powered >= self.tm else 0
        self.budget += profit
        
        # Reduce lifespan of resources
        for res in self.active_resources:
            res.remaining_life -= 1
            if res.remaining_life <= 0:
                res.is_active = False
        
        return f"End of turn - Budget: {self.budget}, Buildings powered: {total_powered}, Profit: {profit}"


file_path = "../1-thunberg.txt"
D, R, T, resources, turns = parse_input_file(file_path)

# Example usage
game = GameSimulator(initial_budget=1000, tm=10, tx=20, tr=5)
game.purchase_resource(Resource('R1', 'A', 100, 10, 5, 5, 50, 5))
game.purchase_resource(Resource('R2', 'D', 200, 20, 8, 6, -30, 4))

turns = 100
for turn in range(turns):
    print(f"Turn {turn+1}: {game.simulate_turn()}")
