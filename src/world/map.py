import random
import pyray as pr


class GameMap:
    def __init__(self, cols=20, rows=20, tree_density=0.15):
        self.cols = cols
        self.rows = rows
        self.tree_density = tree_density  # Percentage of tiles that become trees (0.15 = 15%)

        # Center of a tile offset to position things nicely
        self.tile_size = 2.0
        self.grid = []
        self.generate_forest()

    def generate_forest(self):
        """Generates a flat 2D grid matrix distributing grass and trees randomly."""
        self.grid = []
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                # Ensure the starting area around (0,0) / center is kept clear of trees
                is_center = (abs(c - self.cols // 2) <= 1 and abs(r - self.rows // 2) <= 1)

                if not is_center and random.random() < self.tree_density:
                    row_data.append(1)  # Tree obstacle
                else:
                    row_data.append(0)  # Walkable Grass
            self.grid.append(row_data)

        # src/world/map.py

    def render(self):
        """
        Iterates over the 2D grid matrix and renders 3D environments.
        Applies a half-tile pivot compensation so visuals lock cleanly into hitboxes.
        """
        # Reconstruct alignment offsets matching your coordinate translation space
        offset_x = (self.cols * self.tile_size) / 2.0
        offset_z = (self.rows * self.tile_size) / 2.0

        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate the raw top-left bounds point on the map plain
                world_x = (col * self.tile_size) - offset_x
                world_z = (row * self.tile_size) - offset_z

                if self.grid[row][col] == 1:
                    # FIX: Shift the visual center out by half a tile size
                    # to align perfectly over the top-left based collision box!
                    render_x = world_x + (self.tile_size / 2.0)
                    render_z = world_z + (self.tile_size / 2.0)

                    # Tree trunk placeholder height settings
                    cube_height = 2.0
                    render_y = cube_height / 2.0  # Keep bottom flush on floor

                    # Draw the obstacle cube
                    pr.draw_cube(
                        pr.Vector3(render_x, render_y, render_z),
                        self.tile_size,
                        cube_height,
                        self.tile_size,
                        pr.GREEN
                    )
                    pr.draw_cube_wires(
                        pr.Vector3(render_x, render_y, render_z),
                        self.tile_size,
                        cube_height,
                        self.tile_size,
                        pr.DARKGREEN
                    )
                else:
                    # Optional: Draw empty ground floor tile outlines/flats if desired
                    pass
