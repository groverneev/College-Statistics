from __future__ import annotations

YEAR_SUBAGENT_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["year", "data", "notes"],
    "properties": {
        "year": {"type": "string"},
        "data": {
            "type": "YearData",
            "schema_ref": "src/lib/types.ts#YearData",
        },
        "notes": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}


def build_year_subagent_prompt(*, school_name: str, year: str) -> str:
    return (
        f"Review all screenshots for {school_name} {year} and return one strict JSON object with keys "
        '"year", "data", and "notes". '
        'The "data" object must match the site\'s YearData schema in src/lib/types.ts exactly. '
        "Use only values that are visibly supported by the screenshots. "
        "Derive acceptanceRate, yield, total enrollment, and totalCOA when the required source values are visible. "
        "If an optional field is not visible, omit it. "
        "If a required field cannot be recovered safely, do not guess; note the gap in notes. "
        "Return JSON only."
    )
