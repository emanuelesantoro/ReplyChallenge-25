import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def parse_input_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    
    # Parse first line (D, R, T)
    D, R, T = map(int, lines[0].split())
    
    # Parse resources
    resources = []
    for i in range(1, R + 1):
        parts = lines[i].split()
        resource = {
            "RIr": int(parts[0]), "RAr": int(parts[1]), "RPr": int(parts[2]),
            "RWr": int(parts[3]), "RMr": int(parts[4]), "RLr": int(parts[5]),
            "RUr": int(parts[6]), "RTr": parts[7],
            "REr": int(parts[8]) if len(parts) > 8 else None
        }
        resources.append(resource)
    
    # Parse turns
    turns = []
    for i in range(R + 1, R + 1 + T):
        TMt, TXt, TRt = map(int, lines[i].split())
        turns.append({"TMt": TMt, "TXt": TXt, "TRt": TRt})
    
    return D, R, T, resources, turns

level = "1-thunberg"

D, R, T, resources, turns = parse_input_file(f"{level}.txt")

# Print parsed data
print("Initial Capital:", D)
print("Total Resources:", R)
print("Game Turns:", T)
print("Resources:", resources)
print("Turns:", turns)

content = "ciao"

with open(f"{level[0]}.txt", "w") as file:
    file.write(content)
