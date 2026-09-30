import subprocess, uuid

IMAGE = "python:3.12-slim"

def run_code(code: str, timeout: int = 10) -> tuple[bool, str]:
    """Run Python code in a throwaway Docker container. No network, capped memory/CPU/processes."""
    name = f"agent-{uuid.uuid4().hex[:8]}"
    cmd = ["docker", "run", "--rm", "-i", "--name", name, "--network", "none",
           "--memory", "256m", "--cpus", "0.5", "--pids-limit", "64",
           "--read-only", "--tmpfs", "/tmp", IMAGE, "python", "-"]
    try:
        p = subprocess.run(cmd, input=code, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
        return False, f"TimeoutError: code ran longer than {timeout}s"
    return p.returncode == 0, (p.stdout + p.stderr)[-2000:]
