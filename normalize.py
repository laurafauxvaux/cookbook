def recipe_name_to_id(recipe_name):
    to_normalize = recipe_name.strip().lower()

    recipe_id = ""

    for chara in to_normalize:
        if chara.isalnum():
            recipe_id += chara
        elif (
            chara == " "
            or chara == "-"
            or chara == "_"
            ):
            if recipe_id and recipe_id[-1] == "_":
                continue
            recipe_id += "_"
        

    return recipe_id.rstrip("_")
        
    
    
