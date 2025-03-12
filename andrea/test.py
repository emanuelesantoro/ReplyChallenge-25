import os

level = "1-thunberg"
# Move to the directory where the script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open(f"{level}.txt", "r") as file:
    content = file.read()

content = """
0 1 5
1 1 2
2 1 2
4 2 2 2
5 1 2
"""

with open(f"{level[0]}.txt", "w") as file:
    file.write(content)
