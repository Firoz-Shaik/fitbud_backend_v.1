# The "source of truth" for all unit conversions, kept in the backend.
UNIT_DICTIONARY = {
    # Mass Units
    "grams":    {"type": "MASS",   "to_base_grams": 1.0},
    "g":        {"type": "MASS",   "to_base_grams": 1.0},
    "kg":       {"type": "MASS",   "to_base_grams": 1000.0},
    "oz":       {"type": "MASS",   "to_base_grams": 28.35},
    "lb":       {"type": "MASS",   "to_base_grams": 453.592},
    # Volume Units
    "ml":       {"type": "VOLUME", "to_base_ml": 1.0},
    "liter":    {"type": "VOLUME", "to_base_ml": 1000.0},
    "fl oz":    {"type": "VOLUME", "to_base_ml": 29.5735},
    "cup":      {"type": "VOLUME", "to_base_ml": 236.588},
    "tbsp":     {"type": "VOLUME", "to_base_ml": 14.787},
    "tsp":      {"type": "VOLUME", "to_base_ml": 4.929},
}


def calculate_nutrition(food_item, serving_size: float, serving_unit: str) -> dict:
    """
    Calculate nutrition for a serving. food_item must have calories_per_100g,
    protein_per_100g, carbs_per_100g, fat_per_100g, base_unit_type, grams_per_ml.
    """
    unit_info = UNIT_DICTIONARY.get((serving_unit or "g").lower())
    if not unit_info:
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

    total_grams = 0.0
    if unit_info["type"] == "MASS":
        total_grams = serving_size * unit_info["to_base_grams"]
    elif unit_info["type"] == "VOLUME":
        bt = getattr(food_item, "base_unit_type", None)
        gpm = getattr(food_item, "grams_per_ml", None)
        if bt == "VOLUME" and gpm:
            total_ml = serving_size * unit_info["to_base_ml"]
            total_grams = total_ml * float(gpm)
        else:
            return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

    multiplier = total_grams / 100.0
    return {
        "calories": (getattr(food_item, "calories_per_100g", None) or 0) * multiplier,
        "protein_g": float(getattr(food_item, "protein_per_100g", None) or 0) * multiplier,
        "carbs_g": float(getattr(food_item, "carbs_per_100g", None) or 0) * multiplier,
        "fat_g": float(getattr(food_item, "fat_per_100g", None) or 0) * multiplier,
    }