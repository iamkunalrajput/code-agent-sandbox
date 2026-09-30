import json
from agent import solve

tasks = json.load(open("tasks.json"))
results = [solve(t["task"], check=lambda out, e=t["expect"]: e in out) for t in tasks]
passed = [r for r in results if r["success"]]
first_try = sum(r["attempts"] == 1 for r in passed)
print(f"solved {len(passed)}/{len(tasks)} | first try {first_try} | recovered after error {len(passed) - first_try}")
