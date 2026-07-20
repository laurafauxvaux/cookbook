import pprint
from config import RECIPES_FILE, INGREDIENTS_FILE
from ingredients import (
    VALID_UNITS, 
    Ingredient,
    add_ingredient_to_catalog,
    ingredient_exists,
    get_ingredient_id_from_name,
    load_ingredients,
    save_ingredients
    )
from normalize import name_to_id
from recipes import (
    Recipe,
    RecipeIngredient, 
    load_recipes, 
    recipe_search,
    view_recipe,
    add_recipe_to_cookbook,
    recipe_exists,
    save_recipe,
    modify_recipe,
    delete_recipe
    )


def create_recipe(recipes, ingredients_catalog):
    recipe_name = input("Enter a new recipe name: ")
    recipe_id = name_to_id(recipe_name)
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

    instructions = input(
        "Enter instructions. Please separate steps by semi-colons (e.g Melt butter;Add flour): "
        ).strip().split(";")
    
    ingredients = collect_recipe_ingredients(ingredients_catalog)

    recipe: Recipe = {
        "en": recipe_name,
        "ingredients": ingredients,
        "instructions": instructions
        }

    if aliases is not None:
        recipe["aliases"] = aliases
    
        
    return recipe_id, recipe


def collect_recipe_ingredients(ingredients_catalog:dict[str, Ingredient])->list[RecipeIngredient]:
    entered_ingredients = input("Enter ingredients. Please separate steps by semi-colons: ").strip().split(";")
    known_ingredients: list[str] = []
    unknown_ingredient: list[str] = []
    recipe_ingredients: list[RecipeIngredient] = []

    for ingredient in entered_ingredients:
        ingredient = ingredient.strip()
        ingredient_id = get_ingredient_id_from_name(ingredients_catalog, ingredient)
        if ingredient_id is None:
            unknown_ingredient.append(ingredient)
        else:
           known_ingredients.append(ingredient_id)
    
    if unknown_ingredient:
        create_ingredient_choice = input(
            f"Unknown ingredients: {', '.join(unknown_ingredient)}. Creation is needed to save your recipe. Create? (Y/N): "
            ).strip().upper()
        if create_ingredient_choice not in ("Y", "N"):
            raise ValueError("Invalid input. Please enter 'Y' or 'N'.")
        if create_ingredient_choice == "Y":
            for ingredient in unknown_ingredient:
                ingredient_id, ingredient = create_ingredient(ingredients_catalog, ingredient_name=ingredient)
                add_ingredient_to_catalog(ingredients_catalog, ingredient_id, ingredient)
                if ingredient_id not in known_ingredients:
                    known_ingredients.append(ingredient_id)
            save_ingredients(INGREDIENTS_FILE, ingredients_catalog)
        else:
            raise ValueError("Cannot save recipe without creating unknown ingredients.")
    
    for ingredient_id in known_ingredients:
        quantity = float(input(f"Enter quantity for {ingredient_id}: "))
        recipe_ingredient: RecipeIngredient = {
            "ingredient": ingredient_id,
            "quantity": quantity
        }
        recipe_ingredients.append(recipe_ingredient)

    return recipe_ingredients


def create_ingredient(ingredients_catalog:dict[str, Ingredient], ingredient_name:str | None = None)->tuple[str, Ingredient]:
    if ingredient_name is None:
        ingredient_name = input("Enter a new ingredient name: ")
    ingredient_id = name_to_id(ingredient_name)
    if ingredient_exists(ingredients_catalog, ingredient_id):
         raise ValueError(
             f"{ingredient_id} already in the ingredients catalog."
             )
    
    add_aliases = input(
        "Would you like to add aliases to this ingredient's name? (Y/N): "
        ).strip().upper()
    aliases = None
    if add_aliases == "Y":
        aliases = input(
            "Enter an alias. If several, separate by commas: "
            ).strip().split(",")

    unit = input(f"Unit {VALID_UNITS}: ").strip().lower()
    if unit not in VALID_UNITS:
        raise ValueError(f"Invalid unit. Please choose from {VALID_UNITS}.")
    is_vegan = input("Is this ingredient vegan? (Y/N): ").strip().upper()
    if is_vegan not in ("Y", "N"):
        raise ValueError("Invalid input. Please enter 'Y' or 'N'.")
    if is_vegan == "Y":
        is_vegan = True
    else:
        is_vegan = False
    ingredient: Ingredient = {
        "en": ingredient_name,
        "base_unit": unit,
        "is_vegan": is_vegan
    }
    if aliases is not None:
        ingredient["aliases"] = aliases

    return ingredient_id, ingredient


def main():
    try:
        recipes = load_recipes(RECIPES_FILE)
    except FileNotFoundError:
        print("Error: recipes.json can't be found.")
        return
    
    try:
        ingredients_catalog = load_ingredients(INGREDIENTS_FILE)
    except FileNotFoundError:
        print("Error: ingredients.json can't be found.")
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
                    if create not in ("Y", "N"):
                        raise ValueError("Invalid input. Please enter 'Y' or 'N'.")
                    if create.strip().upper() == "Y":
                        recipe_id, recipe = create_recipe(recipes, ingredients_catalog)
                else:
                    pprint.pp(view_recipe(recipes, recipe_id))
            case 2:
                recipe_id, recipe = create_recipe(recipes, ingredients_catalog)
                add_recipe_to_cookbook(recipes, recipe_id, recipe)
                save_recipe(RECIPES_FILE, recipes)
            case 3:
                to_modify_name = input("Enter the name of the recipe you wish to modify: ")
                recipe_id = recipe_search(recipes, to_modify_name)
                print("1. Name")
                print("2. Aliases")
                print("3. Ingredients")
                print("4. Instructions")
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
                        new_ingredients = collect_recipe_ingredients(ingredients_catalog)
                        modify_recipe(recipes, recipe_id, "ingredients", new_ingredients)
                        save_recipe(RECIPES_FILE, recipes)
                    case 4:
                        new_instructions = input(
                            "Enter new instructions. Please separate steps by semi-colons (e.g Melt butter;Add flour): "
                            ).strip().split(";")
                        modify_recipe(recipes, recipe_id, "instructions", new_instructions)
                        save_recipe(RECIPES_FILE, recipes)
            case 4:
                to_delete_name = input("Enter the name of the recipe you wish to delete: ")
                recipe_id = name_to_id(to_delete_name)
                del_choice = input(f"Are you sure you want to delete {to_delete_name}? (Y/N): ").strip().upper()
                if del_choice not in ("Y", "N"):
                    raise ValueError("Invalid input. Please enter 'Y' or 'N'.")
                if del_choice == "Y":
                    delete_recipe(recipes, recipe_id)
                    save_recipe(RECIPES_FILE, recipes)
            case 0:
                break
            case _:
                print("Invalid choice, please enter a number from the menu list.")

    


if __name__ == "__main__":
    main()
