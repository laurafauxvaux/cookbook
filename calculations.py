from typing import Literal
from recipes import Recipe, RecipeIngredient
from ingredients import Ingredient

USCustomaryUnit = Literal["oz", "fl_oz", "unit"]

def scale_recipe(recipe: Recipe, number_of_servings:int)->list[RecipeIngredient]:
    multiplied_ingredients = []
    ratio = number_of_servings / recipe["servings"]
    for ingredient in recipe["ingredients"]:
        multiplied_ingredients.append({
            "ingredient": ingredient["ingredient"],
            "quantity": ingredient["quantity"] * ratio,
            })
    return multiplied_ingredients

def convert_metric_to_us_customary(ingredient:Ingredient, quantity:float)->tuple[float, USCustomaryUnit]:
    match ingredient["base_unit"]:
        case "g":
            return quantity / 28.3495, "oz"
        case "ml":
           return quantity / 29.5735, "fl_oz"
        case "unit":
            return quantity, "unit"
    