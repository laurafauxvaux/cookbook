import json
from typing import TypedDict, NotRequired, Literal

Unit = Literal["g", "ml", "unit"]

class Ingredient(TypedDict):
    en:str
    aliases: NotRequired[list[str]]
    base_unit: Unit
    is_vegan: bool

def load_ingredients(filepath:str)->dict[str, Ingredient]:
    with open(filepath, "r") as file:
        ingredients = json.load(file)
    return ingredients

def get_ingredient_id_from_name(ingredients:dict[str, Ingredient], ingredient_name:str)->str | None:
    searched = ingredient_name.lower()
    for ingredient_id, ingredient in ingredients.items():
        if (searched == ingredient["en"].lower()
            or searched == ingredient_id
            or any(searched == alias.lower() for alias in ingredient.get("aliases", []))
        ):
                return ingredient_id
    return None

def ingredient_exists(ingredients:dict[str, Ingredient], ingredient_name:str)->bool:
    searched = ingredient_name.lower()
    return get_ingredient_id_from_name(ingredients, searched) is not None

def add_ingredient_to_ingredients(ingredients:dict[str, Ingredient], ingredient_id:str, ingredient:Ingredient):
    ingredients[ingredient_id] = ingredient

def save_ingredient(filepath:str, ingredients:dict[str, Ingredient]):
    with open(filepath, "w") as file:
         json.dump(ingredients, file, indent=4)

def modify_ingredient(ingredients:dict[str, Ingredient], ingredient_id:str, field:str, value:str | list[str] | bool):
     ingredients[ingredient_id][field] = value

def delete_ingredient(ingredients:dict[str, Ingredient], ingredient_id:str):
    del ingredients[ingredient_id]