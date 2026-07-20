def name_to_id(name):
    to_normalize = name.strip().lower()

    id = ""

    for chara in to_normalize:
        if chara.isalnum():
           id += chara
        if id:
            if (
                chara == " "
                or chara == "-"
                or chara == "_"
                ):
                if id[-1] == "_":
                    continue
                id += "_"
        
    return id.rstrip("_")

    
    
