from typing import TypedDict
from config import INGREDIENTS_FILE
from ingredients import (
    VALID_UNITS, 
    Ingredient,
    add_ingredient_to_catalog,
    ingredient_exists,
    get_ingredient_id_from_name,
    save_ingredients
    )
from normalize import name_to_id
from recipes import (
    Recipe,
    RecipeIngredient, 
    view_recipe,
    recipe_exists,
    search_recipes_by_ingredients
    )

from calculations import scale_recipe, convert_metric_to_us_customary

class DisplayIngredient(TypedDict):
    name:str
    quantity:float
    unit:str  


def offer_serving_calculation(recipe:Recipe, 
                              ingredients_catalog:dict[str, Ingredient], 
                              use_us_customary:bool = False)->None:
    if "servings" not in recipe:
        return
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

            displayed_ingredients = display_ingredients(
                recipe,
                ingredients_catalog,
                target_servings=chosen_servings,
                use_us_customary=use_us_customary
            )

            print(
                format_recipe(
                    recipe,
                    chosen_servings,
                    displayed_ingredients,
                )
            )
            break
            
    

def display_ingredients(recipe:Recipe,
                        ingredients_catalog:dict[str, Ingredient], 
                        target_servings: int | None = None, 
                        use_us_customary: bool = False,
                        )->list[DisplayIngredient]:
    displayed_ingredients: list[DisplayIngredient] = []

    if target_servings is not None:
        recipe_ingredients = scale_recipe(recipe, target_servings)
    else:
        recipe_ingredients = recipe["ingredients"]

    for recipe_ingredient in recipe_ingredients:
        ingredient_id = recipe_ingredient["ingredient"]
        ingredient_data = ingredients_catalog[ingredient_id] 
        quantity = recipe_ingredient["quantity"]
        unit = ingredient_data["base_unit"]
        if use_us_customary:
            quantity, unit = convert_metric_to_us_customary(ingredient_data, quantity)

        displayed_ingredients.append({
            "name": ingredient_data["en"],
            "quantity": quantity,
            "unit": unit,          
        }) 

    return displayed_ingredients

def format_recipe(recipe:Recipe, number_of_servings:int | None, 
                  displayed_ingredients:list[DisplayIngredient]) -> str:
    result = f"{recipe['en']}\n"

    if number_of_servings is not None:
        result += f"Servings: {number_of_servings}\n"
    result += f"Ingredients:\n"

    for ingredient in displayed_ingredients:
        quantity = f"{ingredient['quantity']:.2f}".rstrip("0").rstrip(".")
        unit = ingredient['unit'].replace("_", " ")
        result += (
            f"- {quantity} "
            f"{unit} "
            f"{ingredient['name']}\n"
        )

    result += "\nInstructions:\n"

    for number, instruction in enumerate(recipe["instructions"], start = 1):
        result += f"{number}. {instruction}\n"

    return result


def create_recipe(recipes, ingredients_catalog) -> tuple[str, Recipe]:
    recipe_name = input("Enter a new recipe name: ")
    recipe_id = name_to_id(recipe_name)
    if recipe_exists(recipes, recipe_name):
         raise ValueError(
             f"{recipe_id} already in the cookbook. Please use 'search' option."
             )
    while True:
        aliases_choice = input(
            "Would you like to add aliases to this recipe's name? (Y/N): "
            ).strip().upper()
        
        if aliases_choice in ("Y", "N"):
            break
        print("Please enter Y or N.")

    aliases = None
    if aliases_choice == "Y":
        aliases = input(
            "Enter an alias. If several, separate by commas: "
            ).strip().split(",")
        
    servings = input("Number of servings (leave blank if not applicable): ").strip()

    ingredients = collect_recipe_ingredients(ingredients_catalog)

    instructions = input(
        "Enter instructions. Please separate steps by semi-colons (e.g Melt butter;Add flour): "
        ).strip().split(";")
    
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
        ingredient_id = get_ingredient_id_from_name(ingredients_catalog, ingredient)
        if ingredient_id is None:
            quantity = float(input(f"Enter quantity for {ingredient}: "))
            unknown_ingredient.append(ingredient)
        else:
            unit = ingredients_catalog[ingredient_id]["base_unit"]
            quantity = float(input(f"Enter quantity for {ingredient} in {unit}: "))
        entered_ingredients_with_quantities.append((ingredient, quantity))
        
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
    print(f"\nCreating ingredient: {ingredient_name}")
    add_aliases = input(
        f"Would you like to add aliases for {ingredient_name}? (Y/N): "
        ).strip().upper()
    aliases = None
    if add_aliases == "Y":
        aliases = input(
            "Enter an alias. If several, separate by commas: "
            ).strip().split(",")

    unit = input(f"Unit for {ingredient_name} ({VALID_UNITS}): ").strip().lower()
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


def search_recipe_from_user_ingredients(recipes: dict[str, Recipe], ingredients_catalog: dict[str, Ingredient]) -> None:
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
        if 1 <= recipe_number <= len(matching_recipe_ids):
            break
        print("Invalid number.")
    recipe_choice: str = matching_recipe_ids[recipe_number-1]
    recipe = view_recipe(recipes, recipe_choice)

    unit_choice = input("Use US customary units? (Y/N): ").strip().upper()

    if unit_choice not in ("Y", "N"):
        raise ValueError("Invalid input. Please enter 'Y' or 'N'.")

    use_us_customary = unit_choice == "Y"

    displayed_ingredients = display_ingredients(
        recipe,
        ingredients_catalog,
        use_us_customary=use_us_customary
    )

    print(
        format_recipe(
            recipe,
            recipe.get("servings"),
            displayed_ingredients,
        )
    )
    offer_serving_calculation(recipe, ingredients_catalog, use_us_customary)
    input("\nPress Enter to return to the menu...")