from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def load_generation_prompt() -> str:
    return load_prompt("idea_generation")


def load_scoring_prompt() -> str:
    return load_prompt("scoring")


def load_feedback_prompt() -> str:
    return load_prompt("feedback_evaluation")
