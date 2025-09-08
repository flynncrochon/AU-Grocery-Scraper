import json

with open("test_json.txt", "r") as file:
    content = file.read()

sample = json.loads(content)

print(sample)