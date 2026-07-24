# Cookbook

This project is my first personal project in my Boot.dev journey. It is a command-line cookbook where users can view recipes, add their own, or find recipes based on the ingredients they already have.

## Features

- [x] Search and view recipes by name
- [x] Add a recipe
- [x] Modify a recipe (limited; see Future improvements)
- [x] Delete a recipe
- [x] Find recipes based on available ingredients
- [x] Add missing ingredients during recipe creation
- [x] Scale ingredient quantities for a different number of servings
- [x] Display quantities in metric or US customary units
- [x] Navigate through an interactive terminal menu

## Future improvements

- [ ] Ingredient substitutions
- [ ] User profiles with saved preferences and shopping lists
- [ ] French language support
- [ ] Build an alias lookup dictionary
- [ ] Suggest existing ingredients during recipe creation
- [ ] Accent-insensitive search
- [ ] Search with typo tolerance
- [ ] Add, edit, or remove individual aliases
- [ ] Add, edit, or remove individual ingredients
- [ ] Paginate recipe lists

## Installation

This project requires Python 3.13 or later and uses [uv](https://docs.astral.sh/uv/) for dependency management.

Clone the repository:

```bash
git clone https://github.com/laurafauxvaux/cookbook
cd cookbook
```

Install the required dependencies:
```bash
uv sync
```

## Usage

Run the application from the project directory:
```bash
uv run python main.py
```
Use the arrow keys to navigate through the menu and press Enter to select an option.