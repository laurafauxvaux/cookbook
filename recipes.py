import json
from typing import TypedDict, NotRequired
from config import RECIPES_FILE

class RecipeIngredient(TypedDict):
     ingredient: str
     quantity: float
     unit: str

class Recipe(TypedDict):
    en: str
    aliases: NotRequired[list[str]]
    ingredients: list[RecipeIngredient]
    instructions: list[str]


def load_recipes(filepath:str)->dict:
    with open(filepath, "r") as file:
        recipes = json.load(file)
    return recipes


def recipe_search(recipes:dict[str, Recipe], recipe_name:str)->str:
        searched = recipe_name.lower()
        for recipe_id, recipe in recipes.items():
            if (searched == recipe["en"].lower()
                or any(searched == alias.lower() for alias in recipe.get("aliases", []))
                ):
                    return recipe_id
        raise ValueError


def view_recipe(recipes:dict[str, Recipe], recipe_id:str)->Recipe:
     return recipes[recipe_id]
        

def recipe_exists(recipes:dict[str, Recipe], recipe_name:str)->bool:
        searched = recipe_name.lower()
        for recipe in recipes.values():
            if (searched == recipe["en"].lower()
                or any(searched == alias.lower() for alias in recipe.get("aliases", []))
                ):
                    return True
        return False


def add_recipe_to_cookbook(recipes:dict[str, Recipe], recipe_id:str, recipe:Recipe):
    recipes[recipe_id] = recipe


def save_recipe(filepath:str, recipes:dict[str, Recipe]):
    with open(filepath, "w") as file:
         json.dump(recipes, file, indent=4, sort_keys=True)
    
    
def modify_recipe(recipes:dict[str, Recipe], recipe_id:str, field:str, value:str | list[str] | list[RecipeIngredient]):
     recipes[recipe_id][field] = value
          

def delete_recipe(recipes:dict[str, Recipe], recipe_id:str):
    del recipes[recipe_id]
