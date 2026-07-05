from pathlib import Path


def get_prompt(prompt_name: str) -> str:
    return (Path(__file__).resolve().parents[1] / "prompts" / f"{prompt_name}.md").read_text(encoding="utf-8")
