

def get_generation_category(generation_type):
    from src.schemas import GENERATION_CATHEGORY_ORDER

    generation_type_lower = generation_type.lower()

    if generation_type_lower == "timestamp":
        return "timestamp"

    for category in GENERATION_CATHEGORY_ORDER:
        if category in generation_type_lower:
            return category

    return "other"