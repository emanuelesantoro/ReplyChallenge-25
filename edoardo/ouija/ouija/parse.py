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

# Example usage
# file_path = "../1-thunberg.txt"
# D, R, T, resources, turns = parse_input_file(file_path)
# print(f"Initial Budget: {D}, Resources: {R}, Turns: {T}")
# print("Resources:", resources)
# print("Turns:", turns)