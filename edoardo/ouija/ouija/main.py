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
            "Resource ID": int(parts[0]), 
            "Activation Cost": int(parts[1]),  # One-time initial expenditure
            "Periodic Cost": int(parts[2]),    # Recurring maintenance cost per turn
            "Active Turns": int(parts[3]),     # Turns the resource stays active
            "Downtime Turns": int(parts[4]),   # Turns needed for maintenance after a cycle
            "Life Cycle": int(parts[5]),       # Total lifespan of the resource
            "Buildings Powered": int(parts[6]),# Number of buildings it supports per active turn
            "Special Effect": parts[7],        # Unique effect or property
            "Efficiency Rating": int(parts[8]) if len(parts) > 8 else None  # Additional performance metric
        }
        resources.append(resource)
    
    # Parse turns
    turns = []
    for i in range(R + 1, R + 1 + T):
        TMt, TXt, TRt = map(int, lines[i].split())
        turns.append({"Minimum Buildings": TMt, "Maximum Buildings": TXt, "Profit": TRt})
    
    return D, R, T, resources, turns

level = "../1-thunberg"

D, R, T, resources, turns = parse_input_file(f"{level}.txt")

# Print parsed data
print("Initial Capital:", D)
print("Total Resources:", R)
print("Game Turns:", T)
print("Resources:", resources)
print("Turns:", turns)

## GAME SEQUENCE

available_resources = resources.copy()
available_budget = D
active_resources = []

for turn in range(T):
    resources_to_activate = []
    
    ##TODO IMPLEMENT THE SURPLUS OF RESOURCE E

    ## Assert whether at any turn we spent more than we have 
    for resource in resources_to_activate:
        available_budget -= resource["Activation Cost"]
        if available_budget < 0:
            print("Not enough budget")
            break
    for resource in active_resources:
        available_budget -= resource["Periodic Cost"]
        if available_budget < 0:
            print("Not enough budget")
            break

    ## add the resources to the active resources
    for resource in resources_to_activate:
        active_resources.append(resource)
        # available_resources.remove(resource)
    
    ## Check inside the active resources if any of them expired
    for resource in active_resources:
        resource["Active Turns"] -= 1
        if resource["Active Turns"] == 0:
            available_resources.append(resource)
            active_resources.remove(resource)
