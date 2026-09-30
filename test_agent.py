from agent import solve

def test_recovers_from_error():
    replies = iter(["```python\nprint(1/0)\n```", "```python\nprint(42)\n```"])
    run = lambda code: (("1/0" not in code), "42\n" if "1/0" not in code else "ZeroDivisionError")
    r = solve("print 42", llm=lambda m: next(replies), run=run)
    assert r["success"] and r["attempts"] == 2

def test_gives_up_after_max_attempts():
    r = solve("x", llm=lambda m: "```python\nboom\n```", run=lambda c: (False, "NameError"), max_attempts=3)
    assert not r["success"] and r["attempts"] == 3
