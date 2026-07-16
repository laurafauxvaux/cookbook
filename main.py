import json
import pprint
from config import RECIPES_FILE, INGREDIENTS_FILE
from normalize import recipe_name_to_id
from recipes import (
    Recipe, 
    load_recipes, 
    recipe_search,
    view_recipe,
    add_recipe_to_cookbook,
    recipe_exists,
    save_recipe,
    modify_recipe,
    delete_recipe)


def create_recipe(recipes):
    recipe_name = input("Enter a new recipe name: ")
    recipe_id = recipe_name_to_id(recipe_name)
    if recipe_exists(recipes, recipe_name):
         raise ValueError(
             f"{recipe_id} already in the cookbook. Please use 'search' option."
             )
    
    add_aliases = input(
        "Would you like to add aliases to this recipe's name? (Y/N): "
        ).strip().upper()
    aliases = None
    if add_aliases == "Y":
        aliases = input(
            "Enter an alias. If several, separate by commas: "
            ).strip().split(",")
    
    #TODO: ingredients
    
    instructions = input(
        "Enter instructions. Please separate steps by semi-colons (e.g Melt butter;Add flour): "
        ).strip().split(";")
    
    recipe: Recipe = {
        "en": recipe_name,
        #TODO: ingredients
        "instructions": instructions
    }
    if aliases is not None:
        recipe["aliases"] = aliases

    return recipe_id, recipe


def main():
    try:
        recipes = load_recipes(RECIPES_FILE)
    except FileNotFoundError:
        print("Error: recipes.json can't be found.")
        return
    
    while True:
        print("====MENU====")
        print("1. Search recipe")
        print("2. Create recipe")
        print("3. Modify recipe")
        print("4. Delete recipe")
        print("0. Leave")

        choice = int(input("Choice: "))

        match choice:
            case 1:
                recipe_name = input("Enter recipe name: ")
                try:
                    recipe_id = recipe_search(recipes, recipe_name)
                except ValueError:
                    create = input(f"Recipe for {recipe_name} not found. Would you like to create it? (Y/N): ")
                    if create.strip().upper() == "Y":
                        create_recipe(recipes)
                else:
                    pprint.pp(view_recipe(recipes, recipe_id))
            case 2:
                recipe_id, recipe = create_recipe(recipes)
                add_recipe_to_cookbook(recipes, recipe_id, recipe)
                save_recipe(RECIPES_FILE, recipes)
            case 3:
                to_modify_name = input("Enter the name of the recipe you wish to modify: ")
                recipe_id = recipe_name_to_id(to_modify_name)
                print("1. Name")
                print("2. Aliases")
                print("3. Ingredients")
                print("4. Insctructions")
                modify_choice = int(input("You would like to modify: "))
                
                match modify_choice:
                    case 1:
                        new_name = input("Please enter a new name for the recipe: ").strip()
                        modify_recipe(recipes, recipe_id, "en", new_name)
                        save_recipe(RECIPES_FILE, recipes)
                    case 2:
                        new_aliases = input("Enter at least one alias. If several, separate by commas: ").strip().split(",")
                        modify_recipe(recipes, recipe_id, "aliases", new_aliases)
                        save_recipe(RECIPES_FILE, recipes)
                    case 3:
                        #TODO
                    case 4:
                        new_instructions = input(
                            "Enter new instructions. Please separate steps by semi-colons (e.g Melt butter;Add flour): "
                            ).strip().split(";")
                        modify_recipe(recipes, recipe_id, "instructions", new_instructions)
                        save_recipe(RECIPES_FILE, recipes)
            case 4:
                to_delete_name = input("Enter the name of the recipe you wish to delete: ")
                recipe_id = recipe_name_to_id(to_delete_name)
                del_choice = input(f"Are you sure you want to delete {to_delete_name}? (Y/N): ").strip().upper()
                if del_choice == "Y":
                    delete_recipe(recipes, recipe_id)
                    save_recipe(RECIPES_FILE, recipes)
            case 0:
                break
            case _:
                print("Invalid choice, please enter a number from the menu list.")

    


if __name__ == "__main__":
    main()
