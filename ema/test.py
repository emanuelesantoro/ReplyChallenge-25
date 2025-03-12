import os

# Move to the directory where the script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("input.txt", "r") as file:
    content = file.read()

with open("output.txt", "w") as file:
    file.write(content)
