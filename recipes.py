import json
from typing import TypedDict
from config import RECIPES_FILE

class RecipeIngredients(TypedDict):
     ingredient:str
     quantity:float
     unit:str

class Recipe(TypedDict):
    en:str
    aliases:list[str]
    ingredients:list[RecipeIngredients]
    instructions:list[str]


def load_recipes(filepath:str)->dict:
    with open(filepath, "r") as file:
        recipes = json.load(file)
    return recipes


def recipe_search(recipes:dict[str, Recipe], recipe_name:str)->Recipe:
        searched = recipe_name.lower()
        for recipe in recipes.values():
            if (searched == recipe["en"].lower()
                or any(searched == alias.lower() for alias in recipe["aliases"])
                ):
                    return recipe
        raise ValueError(f"Recipe for {recipe_name} not found.")
        
def recipe_exists(recipes:dict[str, Recipe], recipe_name:str)->bool:
        searched = recipe_name.lower()
        for recipe in recipes.values():
            if (searched == recipe["en"].lower()
                or any(searched == alias.lower() for alias in recipe["aliases"])
                ):
                    return True
        return False

def create_recipe(recipes:dict[str, Recipe], recipe_id:str, recipe:Recipe):
    if recipe_exists(recipes, recipe_id):
         raise ValueError(f"{recipe["en"]} already in the cookbook. Please use 'search' option.")
    # TODO : ajouter recette au dict
    # TODO : sauvegarde de la recette dans le fichier
    

def modify_recipe(recipes:dict[str, Recipe], recipe_name:str):
     pass

def delete_recipe(recipes:dict[str, Recipe], recipe_name:str):
    pass
