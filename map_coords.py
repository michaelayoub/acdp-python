import json
import math

POSITION_BLOCK_LENGTH = 192

def landblock_is_indoors(landblock_id: int) -> bool:
    return (landblock_id & 0xFFFF) >= 0x100

def get_global_position(landblock_id: int, x: float, y: float, z: float) -> tuple[float]:
    if landblock_is_indoors(landblock_id):
        return None

    landblock_x = landblock_id >> 24 & 0xFF
    landblock_y = landblock_id >> 16 & 0xFF

    global_x = landblock_x * POSITION_BLOCK_LENGTH + x
    global_y = landblock_y * POSITION_BLOCK_LENGTH + y
    global_z = z

    return (global_x, global_y, global_z)

def map_coords(position: tuple[float]) -> tuple[float]:
    if position is None:
        return None
    pos_x, pos_y, _ = position

    coords_x = pos_x / 240.0 - 102
    coords_y = pos_y / 240.0 - 102

    return coords_x, coords_y

def map_coords_str(map_coords: tuple[float]) -> str:
    if map_coords is None:
        return "inside"
    
    coords_x, coords_y = map_coords

    north_south = "N" if coords_y >= 0 else "S"
    east_west = "E" if coords_x >= 0 else "W"

    north_south_str = "{0:.1f}".format(abs(coords_y) - 0.05) + north_south
    east_west_str = "{0:.1f}".format(abs(coords_x) - 0.05) + east_west

    return north_south_str + ", " + east_west_str

def cell_dist(pos1: tuple[float], pos2: tuple[float]):
    # only valid if both outside
    x1, y1, _ = pos1

    return max(x1, y1)

def distance(lb1, pos1, lb2, pos2):
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    if lb1 == lb2:
        dx = x1 - x2
        dy = y1 - y2
        dz = z1 - z2
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    else:
        lb1_x = lb1 >> 24 & 0xFF
        lb1_y = lb1 >> 16 & 0xFF
        lb2_x = lb2 >> 24 & 0xFF
        lb2_y = lb2 >> 16 & 0xFF
        dx = (lb1_x - lb2_x) * POSITION_BLOCK_LENGTH + x1 - x2
        dy = (lb1_y - lb2_y) * POSITION_BLOCK_LENGTH + y1 - y2
        dz = z1 - z2
        return math.sqrt(dx*dx + dy*dy + dz*dz)

def process_pois(write_out=False):
    pois = {}
    with open("pois.json", "r") as f:
        pois = json.load(f)["pois"]
    
    outdoor_pois = [poi for poi in pois if not landblock_is_indoors(poi['obj_Cell_Id'])]

    if write_out:
        with open("outdoor_pois.json", "w") as f:
            json.dump(outdoor_pois, f)

    poi_map = {}
    for poi in outdoor_pois:
        poi_map[poi["name"]] = poi

    return poi_map

def poi_distance(poi1, poi2):
    return distance(
        poi1["obj_Cell_Id"],
        (poi1["origin_X"], poi1["origin_Y"], poi1["origin_Z"]),
        poi2["obj_Cell_Id"],
        (poi2["origin_X"], poi2["origin_Y"], poi2["origin_Z"])
    )



if __name__ == "__main__":
    landblock_id = 2880634900
    x = 50.0280151367187
    y = 95.1958694458007
    z = 64.1740036010742
    print(map_coords_str(map_coords(get_global_position(landblock_id, x, y, z))))

    landblock_id = 2880635138
    x = 84.3781356811523
    y = 106.862091064453
    z = 65.2050018310546
    print(map_coords_str(map_coords(get_global_position(landblock_id, x, y, z))))

    landblock_id = 2847146009
    x = 85.1532974243164
    y = 14.3854999542236
    z = 94.0050048828125
    print(map_coords_str(map_coords(get_global_position(landblock_id, x, y, z))))

    landblock_id = 0x5B9C0000
    x = 104.737000
    y = 107.132004 
    z = 14.005000
    print(map_coords_str(map_coords(get_global_position(landblock_id, x, y, z)))) # 23.2N, 28.7W

    landblock_id = 722534415
    x = 26.76373
    y = 156.8049
    z = 60.05038
    print(map_coords_str(map_coords(get_global_position(landblock_id, x, y, z)))) # 87.7S, 67.4W

    outdoor_pois_map = process_pois()
    
    shoushi_poi = outdoor_pois_map.get("Shoushi")
    hebian_to_poi = outdoor_pois_map.get("Hebian-to")

    dist = poi_distance(shoushi_poi, hebian_to_poi)

    print(dist)

    Zaikhal = outdoor_pois_map.get("Zaikhal")
    AlJalima = outdoor_pois_map.get("Al-Jalima")
    dist = poi_distance(Zaikhal, AlJalima)
    print(dist)

    tufa = outdoor_pois_map.get("Tufa")
    dist = poi_distance(Zaikhal, tufa)
    print(dist)

    Ayan = outdoor_pois_map.get("Ayan Baqur")
    cell = Ayan['obj_Cell_Id']
    x = Ayan['origin_X']
    y = Ayan['origin_Y']
    z = Ayan['origin_Z']
    print(map_coords_str(map_coords(get_global_position(cell, x, y, z))))