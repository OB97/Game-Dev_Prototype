# src/utils/collision.py

def is_colliding_with_map(position_x, position_z, width, depth, game_map):
    """
    Checks if an entity's bounding box overlaps with any solid tiles (1) in the map.
    Converts 3D centered world space back into 2D top-left based grid indices.
    """
    map_grid = game_map.grid
    tile_size = game_map.tile_size
    cols = game_map.cols
    rows = game_map.rows

    # Reconstruct the identical coordinate alignment offsets from map.py
    offset_x = (cols * tile_size) / 2.0
    offset_z = (rows * tile_size) / 2.0

    # Calculate the bounding box edges in 3D world space
    left = position_x - (width / 2.0)
    right = position_x + (width / 2.0)
    top = position_z - (depth / 2.0)
    bottom = position_z + (depth / 2.0)

    # REVERSE THE OFFSET: Transform world space back into raw 0-start array space
    left_array = left + offset_x
    right_array = right + offset_x
    top_array = top + offset_z
    bottom_array = bottom + offset_z

    # Convert positions to integer grid tile indexes
    min_tile_x = int(left_array // tile_size)
    max_tile_x = int(right_array // tile_size)
    min_tile_y = int(top_array // tile_size)
    max_tile_y = int(bottom_array // tile_size)

    # Protect against index out-of-bounds crashes
    start_x = max(0, min_tile_x)
    end_x = min(cols - 1, max_tile_x)
    start_y = max(0, min_tile_y)
    end_y = min(rows - 1, max_tile_y)

    # Fallback checking boundary: if the box sits completely outside the array, count it as solid
    if min_tile_x < 0 or max_tile_x >= cols or min_tile_y < 0 or max_tile_y >= rows:
        return True

    # Scan the local cluster of grid tiles
    for y in range(start_y, end_y + 1):
        for x in range(start_x, end_x + 1):
            if map_grid[y][x] == 1:
                return True

    return False
