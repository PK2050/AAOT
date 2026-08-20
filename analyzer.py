
"""Analyze customer feedback locally with Ollama and Mistral."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

import ollama
from pydantic import BaseModel, Field, ValidationError


MODEL_NAME = "mistral"
DEFAULT_OUTPUT = Path("feedback_result.json")


class FeedbackAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    category: str = Field(min_length=1)
    priority: Literal["low", "medium", "high", "critical"]
    issue: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)
   
    color: Literal["Red","Black"]
    flower: str= Field(min_length=1)




def analyze_feedback(feedback: str, model: str = MODEL_NAME) -> FeedbackAnalysis:
    """Ask the local model for a schema-constrained analysis and validate it."""
    feedback = feedback.strip()
    if not feedback:
        raise ValueError("Feedback cannot be empty.")

    schema = FeedbackAnalysis.model_json_schema()
    prompt = f"""Analyze the customer feedback below.

Return only JSON matching this schema:
{json.dumps(schema, indent=2)}

Use a concise category such as performance, usability, billing, support,
feature_request, reliability, or other. Base priority on customer impact.

Customer feedback:
{feedback}
"""

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a careful customer feedback analyst.",
            },
            {"role": "user", "content": prompt},
        ],
        format=schema,
        options={"temperature": 0.2},
    )

    content = response.message.content
    if not content:
        raise RuntimeError("The model returned an empty response.")

    return FeedbackAnalysis.model_validate_json(content)


def save_result(
    feedback: str, analysis: FeedbackAnalysis, output_path: Path
) -> dict[str, str]:
    """Save the original feedback and validated analysis as readable JSON."""
    result = {"feedback": feedback, **analysis.model_dump()}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze customer feedback locally with Ollama and Mistral."
    )
    parser.add_argument(
        "feedback",
        nargs="?",
        help="Feedback text. If omitted, the program asks for it interactively.",
    )
    parser.add_argument("--model", default=MODEL_NAME, help="Ollama model name")
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    feedback = args.feedback or input("Enter customer feedback: ").strip()

    try:
        analysis = analyze_feedback(feedback, args.model)
        result = save_result(feedback, analysis, args.output)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except ollama.ResponseError as exc:
        if exc.status_code == 404:
            print(
                f"Model '{args.model}' was not found. Run: ollama pull {args.model}",
                file=sys.stderr,
            )
        else:
            print(f"Ollama error: {exc}", file=sys.stderr)
        return 1
    except (ConnectionError, OSError) as exc:
        print(
            "Cannot connect to Ollama. Make sure the Ollama app is running. "
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 1
    except ValidationError as exc:
        print(f"The model response did not match the required schema:\n{exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved to: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
