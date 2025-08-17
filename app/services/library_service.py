# app/services/library_service.py (NEW FILE)
# Provides static library data for the V1 plan builder.

class LibraryService:
    def get_exercises(self):
        """Returns a static list of common exercises."""
        return [
            {"id": "ex_001", "name": "Barbell Squat", "description": "A compound exercise for the legs and glutes."},
            {"id": "ex_002", "name": "Bench Press", "description": "A compound exercise for the chest, shoulders, and triceps."},
            {"id": "ex_003", "name": "Deadlift", "description": "A compound exercise for the back, legs, and glutes."},
            {"id": "ex_004", "name": "Overhead Press", "description": "A compound exercise for the shoulders and triceps."},
            {"id": "ex_005", "name": "Pull Up", "description": "A bodyweight exercise for the back and biceps."},
            {"id": "ex_006", "name": "Dumbbell Row", "description": "A compound exercise for the back and biceps."},
            {"id": "ex_007", "name": "Plank", "description": "An isometric core strength exercise."},
        ]

    def get_meal_items(self):
        """Returns a static list of common food items."""
        return [
            {"id": "food_001", "name": "Chicken Breast", "category": "Protein"},
            {"id": "food_002", "name": "Salmon Fillet", "category": "Protein"},
            {"id": "food_003", "name": "Brown Rice", "category": "Carbohydrate"},
            {"id": "food_004", "name": "Sweet Potato", "category": "Carbohydrate"},
            {"id": "food_005", "name": "Avocado", "category": "Fat"},
            {"id": "food_006", "name": "Olive Oil", "category": "Fat"},
            {"id": "food_007", "name": "Broccoli", "category": "Vegetable"},
            {"id": "food_008", "name": "Spinach", "category": "Vegetable"},
        ]

library_service = LibraryService()