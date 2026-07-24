from simple_term_menu import TerminalMenu
from config import RECIPES_FILE, INGREDIENTS_FILE
from ingredients import load_ingredients 
from normalize import name_to_id
from recipes import (
    load_recipes, 
    recipe_search,
    view_recipe,
    add_recipe_to_cookbook,
    save_recipe,
    modify_recipe,
    delete_recipe,
    )
from interface import (
                    create_recipe, 
                    collect_recipe_ingredients, 
                    format_recipe, 
                    search_recipe_from_user_ingredients, 
                    display_ingredients,
                    offer_serving_calculation,
                    )

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
    menu_options = [
        "Search recipe by name",
        "Search recipe by ingredients",
        "Create recipe",
        "Modify recipe",
        "Delete recipe",
        "Leave",
    ]
    menu_choices = [1, 2, 3, 4, 5, 0]
    terminal_menu = TerminalMenu(
        menu_options,
        title="====MENU====",
    )
    while True:
        selected_index = terminal_menu.show()
        if selected_index is None:
            break

        choice = menu_choices[selected_index]

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
                    if create == "Y":
                        recipe_id, recipe = create_recipe(recipes, ingredients_catalog)
                        add_recipe_to_cookbook(recipes, recipe_id, recipe)
                        save_recipe(RECIPES_FILE, recipes)
                else:
                    recipe = view_recipe(recipes, recipe_id)
                    number_of_servings = recipe.get("servings")
                    unit_choice = input("Use US customary units? (Y/N): ").strip().upper()
                    if unit_choice not in ("Y", "N"):
                         raise ValueError("Invalid input. Please enter 'Y' or 'N'.")
                    use_us_customary = unit_choice == "Y"
                    displayed_ingredients = display_ingredients(recipe, ingredients_catalog, use_us_customary=use_us_customary)
                    print(
                        format_recipe(
                            recipe,
                            number_of_servings,
                            displayed_ingredients
                        )
                    )

                    offer_serving_calculation(recipe, ingredients_catalog, use_us_customary)

                    input("\nPress Enter to return to the menu...")

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
