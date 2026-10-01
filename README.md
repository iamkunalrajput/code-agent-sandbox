# code-agent-sandbox

![tests](https://github.com/iamkunalrajput/code-agent-sandbox/actions/workflows/test.yml/badge.svg)

A small coding agent. You give it a task in plain English. It writes Python, runs the code in a locked-down Docker container, reads any error, and tries again, up to 3 attempts. If it still fails, it stops and returns the last error.

## Results

20 self-written tasks (primes, dates, JSON, regex, plus tasks that need numpy/pandas, which are not installed, and tasks that time out if written naively). A task passes when the last line printed equals the expected answer exactly.

| Model | First try | Within 3 attempts | Rescued by retry |
|---|---|---|---|
| openai/gpt-oss-120b (Groq free tier) | 19/20 (95%) | 20/20 (100%) | 1 |
| qwen2.5-coder:7b (local, Ollama) | 14/20 (70%) | 18/20 (90%) | 4 |

The retry loop lifted the weaker model from 70% to 90%. One run per model, so treat the numbers as indicative: LLM output varies between runs and 20 tasks is a small sample.

## How it works

1. `agent.py` sends the task to the model and extracts the Python block from the reply.
2. `sandbox.py` runs it in a throwaway container: no network, 256 MB memory, 0.5 CPU, 64 processes, read-only filesystem, 10 s timeout.
3. On a non-zero exit, a timeout or a wrong answer, the error goes back to the model with "fix the code". After 3 attempts the agent gives up.

## Run it

```bash
pip install -r requirements.txt
docker pull python:3.12-slim
pytest                      # unit tests, fake LLM, no Docker or key needed

# eval with any OpenAI-compatible endpoint
LLM_API_KEY=... python eval.py                                  # Groq (default)
LLM_BASE_URL=http://localhost:11434/v1 LLM_MODEL=qwen2.5-coder:7b python eval.py   # local Ollama
```

## Limits

- Only the standard library is available in the sandbox.
- Tasks and expected answers were written by me, not taken from a public benchmark.
- Docker limits reduce risk but are not a full security boundary. Do not run untrusted tasks on a machine you care about.
