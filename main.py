import json
from config import RECIPES_FILE, INGREDIENTS_FILE
from recipes import Recipe, load_recipes







def main():
    try:
        recipes = load_recipes(RECIPES_FILE)
    except FileNotFoundError:
        print("Error: recipes.json can't be found.")
    


if __name__ == "__main__":
    main()
