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