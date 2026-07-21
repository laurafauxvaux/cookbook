import json
import unittest
import shutil
from config import RECIPES_VALID_TEST_FILE, RECIPES_INVALID_TEST_FILE, RECIPES_EMPTY_TEST_FILE, RECIPES_SAVE_TEST_FILE
from recipes import (
    load_recipes,
    save_recipe,
    recipe_search,
    view_recipe,
    recipe_exists,
    add_recipe_to_cookbook,
    modify_recipe,
    delete_recipe,
    search_recipes_by_ingredients
)

class TestRecipes(unittest.TestCase):    

    def test_load_recipes_empty(self):
            recipes = load_recipes(RECIPES_EMPTY_TEST_FILE)
            self.assertEqual(recipes, {})

    def test_load_recipes_valid(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            expected =  {
    "bread": {
            "en": "bread",
            "aliases": ["loaf"],
            "ingredients": [],
            "instructions": []
    },
    "omelette": {
            "en": "omelette",
            "ingredients": [],
            "instructions": []
    }
    }
            self.assertEqual(recipes, expected)
    
    def test_load_recipes_error_no_file(self):
            with self.assertRaises(FileNotFoundError):
                    load_recipes("non_existent_file.json")
    
    def test_load_recipes_error_invalid_json(self):
            with self.assertRaises(json.JSONDecodeError):
                    load_recipes(RECIPES_INVALID_TEST_FILE)

    def test_recipe_search_found(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            recipe_id = recipe_search(recipes, "bread")
            self.assertEqual(recipe_id, "bread")

    def test_recipe_search_found_with_alias(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            recipe_id = recipe_search(recipes, "loaf")
            self.assertEqual(recipe_id, "bread")

    def test_recipe_search_not_found(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            with self.assertRaises(ValueError):
                    recipe_search(recipes, "non_existent_recipe")
    
    def test_view_recipe(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            recipe = view_recipe(recipes, "bread")
            self.assertEqual(recipe, recipes["bread"])
    
    def test_recipe_exists_true(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            self.assertTrue(recipe_exists(recipes, "bread"))

    def test_recipe_exists_false(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            self.assertFalse(recipe_exists(recipes, "non_existent_recipe"))
    
    def test_recipe_exists_alias_true(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            self.assertTrue(recipe_exists(recipes, "loaf"))
    
    def test_add_recipe_to_cookbook(self):
            recipes = load_recipes(RECIPES_VALID_TEST_FILE)
            new_recipe = {
                "en": "banana bread",
                "ingredients": [],
                "instructions": []
            }
            recipe_id = "banana_bread"
            add_recipe_to_cookbook(recipes, recipe_id, new_recipe)
            self.assertIn(recipe_id, recipes)
            self.assertEqual(recipes[recipe_id], new_recipe)

    def test_save_recipe(self):
        shutil.copy(RECIPES_VALID_TEST_FILE,RECIPES_SAVE_TEST_FILE)
        temp_recipes = load_recipes(RECIPES_SAVE_TEST_FILE)
        new_recipe = {
                "en": "banana bread",
                "ingredients": [],
                "instructions": []
            }
        recipe_id = "banana_bread"
        add_recipe_to_cookbook(temp_recipes, recipe_id, new_recipe)
        expected = temp_recipes
        save_recipe(RECIPES_SAVE_TEST_FILE, temp_recipes)
        saved_recipes = load_recipes(RECIPES_SAVE_TEST_FILE)
        self.assertEqual(expected, saved_recipes)

    def test_modify_recipe(self):
        shutil.copy(RECIPES_VALID_TEST_FILE,RECIPES_SAVE_TEST_FILE)
        recipes = load_recipes(RECIPES_SAVE_TEST_FILE)
        modify_recipe(recipes, "omelette", "aliases", ["eggs"])
        save_recipe(RECIPES_SAVE_TEST_FILE, recipes)
        modified_recipes = load_recipes(RECIPES_SAVE_TEST_FILE)
        self.assertEqual(modified_recipes["omelette"]["aliases"], ["eggs"])

    def test_delete_recipe(self):
        shutil.copy(RECIPES_VALID_TEST_FILE,RECIPES_SAVE_TEST_FILE)
        recipes = load_recipes(RECIPES_SAVE_TEST_FILE)
        delete_recipe(recipes, "bread")
        save_recipe(RECIPES_SAVE_TEST_FILE, recipes)
        modified_recipes = load_recipes(RECIPES_SAVE_TEST_FILE)
        self.assertNotIn("bread", modified_recipes)
        
    def test_search_recipes_by_ingredients(self):
        recipes_catalog = {
            "bread": {
                "en": "Bread",
                "ingredients": [
                            {"ingredient": "flour", "quantity": 250.0},
                            {"ingredient": "water", "quantity": 100.0},
                    ],
                "instructions": [],
            },
            "omelette": {
                "en": "Omelette",
                "ingredients": [
                    {"ingredient": "eggs", "quantity": 2.0},
                ],
                "instructions": [],
            },
        }
        result = search_recipes_by_ingredients(recipes_catalog, ["flour", "water"])
        self.assertEqual(result, ["bread"])