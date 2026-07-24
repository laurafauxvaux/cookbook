import unittest
from unittest.mock import patch
from ingredients import Ingredient
from recipes import Recipe
from interface import (DisplayIngredient, create_recipe, 
                       search_recipe_from_user_ingredients, 
                       create_ingredient, 
                       collect_recipe_ingredients,
                       display_ingredients,
                       format_recipe,
                       offer_serving_calculation,
                       )

class TestInterface(unittest.TestCase):

    def test_create_ingredient(self):
            ingredients_catalog = {}
            with patch(
                "builtins.input",
                side_effect=["N", "g", "Y"]
            ):
                ingredient_id, ingredient = create_ingredient(ingredients_catalog, ingredient_name="beans")
    
            self.assertEqual(ingredient_id, "beans")
            self.assertEqual(ingredient["base_unit"], "g")
            self.assertEqual(ingredient["is_vegan"], True)
    
    def test_create_ingredient_with_aliases(self):
        ingredients_catalog = {}
        with patch(
            "builtins.input",
            side_effect=[
                "Y", 
                "red meat, ground beef", 
                "g", 
                "N"
                ]
        ):
            ingredient_id, ingredient = create_ingredient(ingredients_catalog, ingredient_name="beef")

        self.assertEqual(ingredient_id, "beef")
        self.assertEqual(ingredient["base_unit"], "g")
        self.assertEqual(ingredient["is_vegan"], False)
        self.assertEqual(ingredient["aliases"], ["red meat", "ground beef"])

    def test_error_create_ingredient_invalid_unit(self):
        ingredients_catalog = {}
        with patch(
            "builtins.input",
            side_effect=["N", "invalid_unit"]
        ):
            with self.assertRaises(ValueError) as context:
                create_ingredient(ingredients_catalog, ingredient_name="milk")
        self.assertIn("Invalid unit", str(context.exception))


    def test_collect_recipe_ingredients_only_unknown_ingredient(self):
        ingredients_catalog = {}
        with patch("interface.save_ingredients"), patch("builtins.input",
            side_effect=[
                "Eggs; honey",
                "2", "20", # quantities for eggs and honey
                "Y", # create unknown ingredients
                "N", "unit", "N", # No aliases, unit, is_vegan for eggs
                "N", "g", "N" # No aliases, unit, is_vegan for honey
                ]
        ):
            recipe_ingredients = collect_recipe_ingredients(ingredients_catalog)
            expected = [
                {"ingredient": "eggs", "quantity": 2.0},
                {"ingredient": "honey", "quantity": 20.0}
            ]
        self.assertIn("eggs", ingredients_catalog)
        self.assertIn("honey", ingredients_catalog)
        self.assertEqual(recipe_ingredients, expected)


    def test_collect_recipe_known_and_unknown_ingredients(self):
        ingredients_catalog = {
            "flour": {"en": "flour", "base_unit": "g", "is_vegan": True}
        }
        with patch("interface.save_ingredients"), patch("builtins.input",
            side_effect=[
                "flour; sugar",
                "100", "50", # quantities for flour and sugar
                "Y", # create unknown ingredient
                "N", "g", "Y" #No aliases, unit, is_vegan for sugar
                ]
        ):
            recipe_ingredients = collect_recipe_ingredients(ingredients_catalog)
            expected = [
                {"ingredient": "flour", "quantity": 100.0},
                {"ingredient": "sugar", "quantity": 50.0}
            ]
        self.assertIn("sugar", ingredients_catalog)
        self.assertEqual(recipe_ingredients, expected)
        
    
    def test_collect_recipe_ingredients_with_only_known_ingredients(self):
        ingredients_catalog = {
            "flour": {"en": "flour", "base_unit": "g", "is_vegan": True},
            "sugar": {"en": "sugar", "base_unit": "g", "is_vegan": True}
        }
        with patch("builtins.input",
            side_effect=[
                "flour; sugar", # ingredients
                "100", "50" # quantities for flour and sugar
                ]
        ):
            recipe_ingredients = collect_recipe_ingredients(ingredients_catalog)
            expected = [
                {"ingredient": "flour", "quantity": 100.0},
                {"ingredient": "sugar", "quantity": 50.0}
            ]
        self.assertEqual(recipe_ingredients, expected)
    

    def test_error_collect_recipe_ingredients_unknown_ingredient_not_created(self):
        ingredients_catalog = {}
        with patch("builtins.input",
            side_effect=[
                "tofu",
                "200", # quantity for tofu
                "N" # do not create unknown ingredient
                ]
        ):
            with self.assertRaises(ValueError) as context:
                collect_recipe_ingredients(ingredients_catalog)
        self.assertIn("Cannot save recipe without creating unknown ingredients", str(context.exception))

    
    def test_create_recipe(self):
        collected_ingredients = [
                {"ingredient": "flour", "quantity": 250.0},
                {"ingredient": "water", "quantity": 100.0}
            ]
        with patch(
            "interface.collect_recipe_ingredients", 
            return_value=collected_ingredients,
                    ), patch(
            "builtins.input", 
            side_effect=["Bread",
                            "N",
                            "", #servings
                            "Mix;Bake"],
            ):
                recipe_id, recipe = create_recipe({}, {})
                
        expected_recipe = {
            "en": "Bread",
            "ingredients": collected_ingredients,
            "instructions": ["Mix", "Bake"],
        }
        self.assertEqual(recipe_id, "bread")
        self.assertEqual(recipe, expected_recipe)
    

    def test_error_create_recipe_duplicate_id(self):
        recipes_catalog = {
            "bread":{
            "en": "Bread", 
            "ingredients": [], 
            "instructions": []
                }
        }
        with patch("builtins.input", side_effect=["Bread"]):
            with self.assertRaises(ValueError) as context:
                create_recipe(recipes_catalog, {})
        self.assertIn(f"bread already in the cookbook.", str(context.exception))
    
    def test_search_recipe_by_user_ingredients_available(self):
        recipes = {
            "bread":{
                "en": "Bread", 
                "ingredients": [], 
                "instructions": []
            },
            "omelette":{
                "en": 
                "Omelette", 
                "ingredients": [], 
                "instructions": []
            },
        }
        ingredients_catalog = {}
        with patch(
            "builtins.input", side_effect=["flour, water", "1", "N", ""],
                    ), patch(
                        "interface.get_ingredient_id_from_name",side_effect=["flour", "water"],
                ), patch(
                    "interface.search_recipes_by_ingredients", return_value=["bread", "omelette"],
                ), patch(
                    "interface.view_recipe",
                ) as mock_view_recipe, patch(
                    "interface.offer_serving_calculation",
                ):
            search_recipe_from_user_ingredients(recipes, ingredients_catalog)
        mock_view_recipe.assert_called_once_with(recipes, "bread")
    
    def test_search_recipe_by_user_ingredients_unavailable(self):
        recipes = {
            "bread":{
                "en": "Bread", 
                "ingredients": [], 
                "instructions": []
            },
            "omelette":{
                "en": 
                "Omelette", 
                "ingredients": [], 
                "instructions": []
            },
        }
        ingredients_catalog = {}
        with patch(
            "builtins.input",
            side_effect=["salt", "N"],
        ), patch(
            "interface.get_ingredient_id_from_name",
            return_value=None,
        ), patch(
            "interface.create_ingredient",
        ) as mock_create_ingredient, patch(
            "interface.search_recipes_by_ingredients",
        ) as mock_search, patch(
            "interface.view_recipe",
        ) as mock_view_recipe:
            search_recipe_from_user_ingredients(recipes, ingredients_catalog)
        mock_create_ingredient.assert_not_called()
        mock_search.assert_not_called()
        mock_view_recipe.assert_not_called()

    def test_display_ingredients_no_conversion(self):
        recipe: Recipe = {
                "en": "Bread", 
                "ingredients": [{
                    "ingredient":"flour",
                    "quantity":250.0,
                },
                {
                    "ingredient": "water",
                    "quantity": 100.0,
                },
            ],
                "instructions": [],
        }
        ingredients_catalog: dict[str, Ingredient] = {
                "flour": {
                    "en": "Flour",
                    "base_unit": "g",
                    "is_vegan": True,
                    },
                "water": {
                    "en": "Water",
                    "base_unit": "ml",
                    "is_vegan": True,
                    },
        }
        result = display_ingredients(recipe, ingredients_catalog)
        expected = [
        {
            "name": "Flour",
            "quantity": 250.0,
            "unit": "g",
        },
        {
            "name": "Water",
            "quantity": 100.0,
            "unit": "ml",
        },
    ]
        self.assertEqual(expected, result)


    def test_display_ingredients_servings_conversion(self):
        recipe: Recipe = {
                "en": "Bread",
                "servings": 4, 
                "ingredients": [{
                    "ingredient":"flour",
                    "quantity":250.0,
                },
                {
                    "ingredient": "water",
                    "quantity": 100.0,
                },
                ],
                "instructions": []
            }
        ingredients_catalog: dict[str, Ingredient] = {
                "flour": {
                    "en": "Flour",
                    "base_unit": "g",
                    "is_vegan": True,
                    },
                "water": {
                    "en": "Water",
                    "base_unit": "ml",
                    "is_vegan": True,
                    },
        }
        result = display_ingredients(
            recipe, 
            ingredients_catalog, 
            target_servings=2)
        expected = [
        {
            "name": "Flour",
            "quantity": 125.0,
            "unit": "g",
        },
        {
            "name": "Water",
            "quantity": 50.0,
            "unit": "ml",
        },
    ]
        self.assertEqual(expected, result)


    def test_display_ingredients_us_units_conversion(self):
        recipe: Recipe = {
                "en": "Bread", 
                "ingredients": [{
                    "ingredient":"flour",
                    "quantity":250.0,
                },
                {
                    "ingredient": "water",
                    "quantity": 100.0,
                },
                ],
                "instructions": []
            }
        ingredients_catalog: dict[str, Ingredient] = {
                "flour": {
                    "en": "Flour",
                    "base_unit": "g",
                    "is_vegan": True,
                    },
                "water": {
                    "en": "Water",
                    "base_unit": "ml",
                    "is_vegan": True,
                    },
        }
        result = display_ingredients(
            recipe, 
            ingredients_catalog,
            use_us_customary=True
            )
        
        self.assertEqual(result[0]["name"], "Flour")
        self.assertEqual(result[0]["unit"], "oz")
        self.assertAlmostEqual(result[0]["quantity"], 8.8185, places = 4)
        self.assertEqual(result[1]["name"], "Water")
        self.assertEqual(result[1]["unit"], "fl_oz")
        self.assertAlmostEqual(result[1]["quantity"], 3.3814, places = 4)


    def test_format_recipe(self):
        recipe: Recipe = {
            "en": "Bread",
            "servings": 4, 
            "ingredients": [{
                "ingredient":"flour",
                "quantity":250.0,
            },
            {
                "ingredient": "water",
                "quantity": 100.0,
            },
            ],
            "instructions": [
                "Mix the ingredients.",
                "Bake the bread.",
            ]
        }
        displayed_ingredients: DisplayIngredient = [
            {
            "name": "Flour",
            "quantity": 250.0,
            "unit": "g"
            },
            {
            "name": "Water",
            "quantity": 100.0,
            "unit": "ml",
            }
        ]

        expected = (
            "Bread\n"
            "Servings: 4\n"
            "Ingredients:\n"
            "- 250 g Flour\n"
            "- 100 ml Water\n"
            "\nInstructions:\n"
            "1. Mix the ingredients.\n"
            "2. Bake the bread.\n"
        )

        result = format_recipe(recipe, 4, displayed_ingredients)

        self.assertEqual(expected, result)


    def test_offer_servings_calculation(self):
        recipe: Recipe = {
            "en": "Bread", 
            "servings": 4,
            "ingredients": [], 
            "instructions": []
            }
        ingredients_catalog: dict[str, Ingredient] = {
                "flour": {
                    "en": "Flour",
                    "base_unit": "g",
                    "is_vegan": True,
                    },
                "water": {
                    "en": "Water",
                    "base_unit": "ml",
                    "is_vegan": True,
                    },
        }

        with (
            patch("builtins.input", side_effect = ["Y", "6"]),
        patch(
            "interface.display_ingredients", return_value = [],
        ) as mock_display_ingredients,
        patch("interface.format_recipe", return_value = "Bread"),
        ):
            offer_serving_calculation(recipe, ingredients_catalog, use_us_customary=True)

        mock_display_ingredients.assert_called_once_with(
            recipe,
            ingredients_catalog,
            target_servings=6,
            use_us_customary=True,
        )
    

    def test_offer_servings_calculation_no_servings(self):
        recipe = {
                "en": "Bread", 
                "ingredients": [], 
                "instructions": []
                },
        ingredients_catalog = {}

        with patch("builtins.input") as mock_input, patch(
            "interface.display_ingredients"
            ) as mock_display_ingredients:
            offer_serving_calculation(recipe, ingredients_catalog)

        mock_input.assert_not_called()
        mock_display_ingredients.assert_not_called()


    def test_offer_servings_calculation_negative_answer(self):
        recipe = {
                "en": "Bread", 
                "servings": 4,
                "ingredients": [], 
                "instructions": [],
                }
        ingredients_catalog = {}

        with patch("builtins.input", return_value = "N"), patch(
            "interface.display_ingredients"
            ) as mock_display_ingredients:
            offer_serving_calculation(recipe, ingredients_catalog)

        mock_display_ingredients.assert_not_called()