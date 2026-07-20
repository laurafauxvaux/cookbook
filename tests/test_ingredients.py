import json
import unittest
import shutil
from config import (
    INGREDIENTS_VALID_TEST_FILE,
    INGREDIENTS_INVALID_TEST_FILE,
    INGREDIENTS_SAVE_TEST_FILE
)
from ingredients import (
    load_ingredients,
    save_ingredients,
    get_ingredient_id_from_name,
    ingredient_exists,
    add_ingredient_to_catalog,
    modify_ingredient,
    delete_ingredient
)
import ingredients

class TestIngredients(unittest.TestCase):

    def test_load_ingredients_valid(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        expected = {
        "eggs": {
            "en": "Eggs", "aliases": ["egg"], "base_unit": "unit", "is_vegan": False
        }, 
        "flour": {
            "en": "Flour", "aliases": [], "base_unit": "g", "is_vegan": True
        }, 
        "milk": {
            "en": "Milk", "aliases": [], "base_unit": "ml", "is_vegan": False
        }
    }
        self.assertEqual(ingredients, expected)
    
    def test_load_ingredients_error_no_file(self):
        with self.assertRaises(FileNotFoundError):
            load_ingredients("non_existent_file.json")
    
    def test_load_ingredients_error_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            load_ingredients(INGREDIENTS_INVALID_TEST_FILE)
    
    def test_get_ingredient_id_from_name_found(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        ingredient_id = get_ingredient_id_from_name(ingredients, "eggs")
        self.assertEqual(ingredient_id, "eggs")
    
    def test_get_ingredient_id_from_name_found_with_different_case(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        ingredient_id = get_ingredient_id_from_name(ingredients, "Eggs")
        self.assertEqual(ingredient_id, "eggs")

    def test_get_ingredient_id_from_name_found_with_alias(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        ingredient_id = get_ingredient_id_from_name(ingredients, "egg")
        self.assertEqual(ingredient_id, "eggs")

    def test_get_ingredient_id_from_name_not_found(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        ingredient_id = get_ingredient_id_from_name(ingredients, "non_existent_ingredient")
        self.assertIsNone(ingredient_id)
    
    def test_ingredient_exists_true(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        exists = ingredient_exists(ingredients, "flour")
        self.assertTrue(exists)
    
    def test_ingredient_exists_false(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        exists = ingredient_exists(ingredients, "non_existent_ingredient")
        self.assertFalse(exists)
    
    def test_add_ingredient_to_catalog(self):
        ingredients = load_ingredients(INGREDIENTS_VALID_TEST_FILE)
        new_ingredient_id = "sugar"
        new_ingredient = {
            "en": "Sugar", "aliases": ["sweetener"], "base_unit": "g", "is_vegan": True
        }
        add_ingredient_to_catalog(ingredients, new_ingredient_id, new_ingredient)
        self.assertIn(new_ingredient_id, ingredients)
        self.assertEqual(ingredients[new_ingredient_id], new_ingredient)

    def test_save_ingredients(self):
        shutil.copy(INGREDIENTS_VALID_TEST_FILE, INGREDIENTS_SAVE_TEST_FILE)
        temp_ingredients = load_ingredients(INGREDIENTS_SAVE_TEST_FILE)
        new_ingredient_id = "sugar"
        new_ingredient = {
            "en": "Sugar", "aliases": ["sweetener"], "base_unit": "g", "is_vegan": True
        }
        add_ingredient_to_catalog(temp_ingredients, new_ingredient_id, new_ingredient)
        expected = temp_ingredients
        save_ingredients(INGREDIENTS_SAVE_TEST_FILE, temp_ingredients)
        saved_ingredients = load_ingredients(INGREDIENTS_SAVE_TEST_FILE)
        self.assertIn(new_ingredient_id, saved_ingredients)
        self.assertEqual(expected, saved_ingredients)

    def test_modify_ingredient(self):
        shutil.copy(INGREDIENTS_VALID_TEST_FILE, INGREDIENTS_SAVE_TEST_FILE)
        temp_ingredients = load_ingredients(INGREDIENTS_SAVE_TEST_FILE)
        ingredient_id = "milk"
        new_value = True
        modify_ingredient(temp_ingredients, ingredient_id, "is_vegan", new_value)
        self.assertEqual(temp_ingredients[ingredient_id]["is_vegan"], new_value)
    
    def test_delete_ingredient(self):
        shutil.copy(INGREDIENTS_VALID_TEST_FILE, INGREDIENTS_SAVE_TEST_FILE)
        temp_ingredients = load_ingredients(INGREDIENTS_SAVE_TEST_FILE)
        ingredient_id = "milk"
        delete_ingredient(temp_ingredients, ingredient_id)
        self.assertNotIn(ingredient_id, temp_ingredients)