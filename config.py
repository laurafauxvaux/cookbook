from pathlib import Path

DATA_DIR = Path("data")
TEST_DIR = Path("tests")
TEST_DATA_DIR = TEST_DIR / "data"

RECIPES_FILE = DATA_DIR / "recipes.json"
INGREDIENTS_FILE = DATA_DIR / "ingredients.json"

RECIPES_VALID_TEST_FILE = TEST_DATA_DIR / "recipes_valid.json"
RECIPES_INVALID_TEST_FILE = TEST_DATA_DIR / "recipes_invalid.json"
RECIPES_EMPTY_TEST_FILE = TEST_DATA_DIR / "recipes_empty.json"