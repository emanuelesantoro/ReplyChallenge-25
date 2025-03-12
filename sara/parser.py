import os

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

