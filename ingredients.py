import json
from typing import TypedDict, NotRequired, Literal, get_args

Unit = Literal["g", "ml", "unit"]
VALID_UNITS = get_args(Unit)

class Ingredient(TypedDict):
    en:str
    aliases: NotRequired[list[str]]
    base_unit: Unit
    is_vegan: bool

def load_ingredients(filepath:str)->dict[str, Ingredient]:
    with open(filepath, "r") as file:
        ingredients = json.load(file)
    return ingredients

def get_ingredient_id_from_name(ingredients_catalog:dict[str, Ingredient], ingredient_name:str)->str | None:
    searched = ingredient_name.strip().lower()
    for ingredient_id, ingredient in ingredients_catalog.items():
        if (searched == ingredient["en"].lower()
            or searched == ingredient_id.lower()
            or any(searched == alias.lower() for alias in ingredient.get("aliases", []))
        ):
                return ingredient_id
    return None

def ingredient_exists(ingredients_catalog:dict[str, Ingredient], ingredient_name:str)->bool:
    return get_ingredient_id_from_name(ingredients_catalog, ingredient_name) is not None

def add_ingredient_to_catalog(ingredients_catalog:dict[str, Ingredient], ingredient_id:str, ingredient:Ingredient):
    ingredients_catalog[ingredient_id] = ingredient

def save_ingredients(filepath:str, ingredients_catalog:dict[str, Ingredient]):
    with open(filepath, "w") as file:
         json.dump(ingredients_catalog, file, indent=4, sort_keys=True)

def modify_ingredient(ingredients_catalog:dict[str, Ingredient], ingredient_id:str, field:str, value:str | list[str] | bool):
     ingredients_catalog[ingredient_id][field] = value

def delete_ingredient(ingredients_catalog:dict[str, Ingredient], ingredient_id:str):
    del ingredients_catalog[ingredient_id]