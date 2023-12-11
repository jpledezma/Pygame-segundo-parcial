import json

def read_tile_map(path: str, separator: str = ",") -> list:
    tile_map = []
    row_list = []
    with open(path, "r", encoding="utf-8") as file:
        while True:
            row = file.readline()
            if row != "":
                row = row.strip()
                row_list = row.split(separator)
                tile_map.append(row_list)
            else:
                break

    return tile_map

def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        sprites_data = json.load(file)

    return sprites_data