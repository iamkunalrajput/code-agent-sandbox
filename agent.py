import re
import os
from openai import OpenAI

# Any OpenAI-compatible endpoint works: Groq (free tier), Ollama (local), Gemini.
MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")
SYSTEM = ("You write Python 3 scripts. Reply with one ```python block and nothing else. "
          "Print the final answer to stdout. Only the standard library is available.")

def call_llm(messages: list[dict]) -> str:
    client = OpenAI(base_url=os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
                    api_key=os.environ.get("LLM_API_KEY", "ollama"))
    r = client.chat.completions.create(model=MODEL, max_tokens=4000,
                                       messages=[{"role": "system", "content": SYSTEM}] + messages)
    return r.choices[0].message.content or ""

def extract_code(text: str) -> str:
    m = re.search(r"```python\n(.*?)```", text, re.S)
    return m.group(1) if m else text

def solve(task: str, llm=call_llm, run=None, max_attempts: int = 3, check=None) -> dict:
    """Generate code, run it, feed errors back, retry. Stops after max_attempts and reports why it failed."""
    if run is None:
        from sandbox import run_code as run
    messages = [{"role": "user", "content": task}]
    for attempt in range(1, max_attempts + 1):
        reply = llm(messages)
        code = extract_code(reply)
        ok, out = run(code)
        if ok and (check is None or check(out)):
            return {"success": True, "attempts": attempt, "code": code, "output": out}
        problem = out if not ok else f"Output was wrong: {out!r}"
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"That failed:\n{problem}\nFix the code."}]
    return {"success": False, "attempts": max_attempts, "code": code, "output": out}
