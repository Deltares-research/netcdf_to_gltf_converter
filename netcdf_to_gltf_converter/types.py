from pydantic import confloat, conlist

NormalizedFloat = confloat(ge=0.0, le=1.0)
"""A float type that is constraint to be between 0.0 and 1.0 (inclusive)."""

Color = conlist(NormalizedFloat, min_items=4, max_items=4)
"""A list type that is constraint to have exactly 4 floats."""