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
    delete_recipe,
    search_recipes_by_ingredients
    )

from calculations import scale_recipe, convert_metric_to_us_customary


def create_recipe(recipes, ingredients_catalog) -> tuple[str, Recipe]:
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
        
    servings = input("Number of servings (leave blank if not applicable): ").strip()
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
    if servings:
        servings = int(servings)
        if servings > 0:
            recipe["servings"] = servings
        else:
            print("Invalid number, servings won't be saved.")
        
    return recipe_id, recipe


def collect_recipe_ingredients(ingredients_catalog:dict[str, Ingredient])->list[RecipeIngredient]:
    entered_ingredients = input("Enter ingredients. Please separate by semi-colons: ").strip().split(";")
    entered_ingredients_with_quantities: list[tuple[str, float]] = []
    unknown_ingredient: list[str] = []
    recipe_ingredients: list[RecipeIngredient] = []

    for ingredient in entered_ingredients:
        ingredient = ingredient.strip()
        quantity = float(input(f"Enter quantity for {ingredient}: "))
        ingredient_id = get_ingredient_id_from_name(ingredients_catalog, ingredient)
        entered_ingredients_with_quantities.append((ingredient, quantity))
        if ingredient_id is None:
            unknown_ingredient.append(ingredient)
    
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
            save_ingredients(INGREDIENTS_FILE, ingredients_catalog)
        else:
            raise ValueError("Cannot save recipe without creating unknown ingredients.")
    
    for ingredient_name, quantity in entered_ingredients_with_quantities:
        ingredient_id = get_ingredient_id_from_name(ingredients_catalog, ingredient_name)
        if ingredient_id is None:
            raise ValueError(f"Ingredient '{ingredient_name}' could not be resolved.")
        recipe_ingredient: RecipeIngredient = {
            "ingredient": ingredient_id,
            "quantity": quantity
        }
        recipe_ingredients.append(recipe_ingredient)

    return recipe_ingredients


def create_ingredient(ingredients_catalog:dict[str, Ingredient], ingredient_name:str)->tuple[str, Ingredient]:
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
        ingredient["aliases"] = [alias.strip() for alias in aliases]

    return ingredient_id, ingredient


def search_recipe_from_user_ingredients(recipes, ingredients_catalog):
    ingredients_research = input(
        "Enter your ingredients. Please separate by commas: "
        ).strip().split(",")
    ingredients_ids = []
    for ingredient in ingredients_research:
        ingredient  = ingredient.strip()
        ingredient_id = get_ingredient_id_from_name(ingredients_catalog, ingredient)
        if ingredient_id is None:
            create_ingredient_choice = input(
                f"Unknown ingredient: {ingredient}. Recipe can't be found. Create ingredient? (Y/N): "
).strip().upper()
            if create_ingredient_choice == "Y":
                ingredient_id, new_ingredient = create_ingredient(ingredients_catalog, ingredient)
                add_ingredient_to_catalog(ingredients_catalog, ingredient_id, new_ingredient)
                save_ingredients(INGREDIENTS_FILE, ingredients_catalog)
                print(f"Creation of {ingredient} complete, please restart your search.")
                return
            return
        ingredients_ids.append(ingredient_id)
    matching_recipe_ids = search_recipes_by_ingredients(recipes, ingredients_ids)
    if not matching_recipe_ids:
        print("No matching recipe found.")
        return
    for number, recipe_id in enumerate(matching_recipe_ids, start = 1):
        print(f"{number}. {recipes[recipe_id]['en']}")
    while True:
        try:
            recipe_number = int(input("Enter its number to see the recipe: "))
        except ValueError:
            print("Please enter a number.")
            continue
        if recipe_number <= 1 or recipe_number <= len(matching_recipe_ids):
            break
        print("Invalid number.")
    recipe_choice = matching_recipe_ids[recipe_number-1]
    pprint.pp(view_recipe(recipes, recipe_choice))


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
        print("1. Search recipe by name")
        print("2. Search recipe by ingredients")
        print("3. Create recipe")
        print("4. Modify recipe")
        print("5. Delete recipe")
        print("0. Leave")

        choices = (0, 1, 2, 3, 4, 5)
        choice = int(input("Choice: "))
        if choice not in choices:
            print("Please enter a valid choice number.")
        match choice:
            case 1:
                recipe_name = input("Enter recipe name: ")
                try:
                    recipe_id = recipe_search(recipes, recipe_name)
                except ValueError:
                    create = input(
                        f"Recipe for {recipe_name} not found. Would you like to create it? (Y/N): "
                        ).strip().upper()
                    if create not in ("Y", "N"):
                        raise ValueError("Invalid input. Please enter 'Y' or 'N'.")
                    if create.strip().upper() == "Y":
                        recipe_id, recipe = create_recipe(recipes, ingredients_catalog)
                else:
                    pprint.pp(view_recipe(recipes, recipe_id))

                    if "servings" in recipes[recipe_id]:

                        while True:
                            change_servings = input(
                                "Calculate for another number of servings? (Y/N): "
                                ).strip().upper()
                            if change_servings not in ("Y", "N"):
                                print("Please enter Y or N.")
                                continue
                            if change_servings == "N":
                                break
                            
                            try:
                                chosen_servings = int(input("Enter the number of servings: "))
                            except ValueError:
                                print("Please enter a number.")
                                continue
                            else:
                                if chosen_servings <= 0:
                                    print("Please enter a number greater than 0.")
                                    continue
                                else:
                                    pprint.pp(
                                        scale_recipe(recipes[recipe_id], chosen_servings)
                                    )
                                break
            case 2:
                search_recipe_from_user_ingredients(recipes, ingredients_catalog)
            case 3:
                recipe_id, recipe = create_recipe(recipes, ingredients_catalog)
                add_recipe_to_cookbook(recipes, recipe_id, recipe)
                save_recipe(RECIPES_FILE, recipes)
            case 4:
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
            case 5:
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
