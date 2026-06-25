import pyray as pr
import math
from src.entities.base_entity import BaseEntity
from src.util.collision import is_colliding_with_map


class Player(BaseEntity):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        super().__init__(x, y, z)
        self.speed = 6.0

        # Dimensions for our 3D bounding box collision footprint
        self.width = 0.8
        self.depth = 0.8
        self.height = 1.2  # Height used for visual cylinder scaling

    def update(self, dt, game_map=None):
        """
        Processes keyboard inputs, applies an isometric angle rotation matrix,
        and executes axis-separated collision checks against the level data.
        """
        # 1. Capture raw WASD keyboard input
        dx = 0.0
        dz = 0.0

        if pr.is_key_down(pr.KEY_W): dz -= 1.0
        if pr.is_key_down(pr.KEY_S): dz += 1.0
        if pr.is_key_down(pr.KEY_A): dx -= 1.0
        if pr.is_key_down(pr.KEY_D): dx += 1.0

        # 2. Rotate the input vector 45 degrees to match the isometric viewpoint
        if abs(dx) > 0.001 or abs(dz) > 0.001:
            length = math.sqrt(dx * dx + dz * dz)
            dx /= length
            dz /= length

            cos_45 = 0.7071
            sin_45 = 0.7071

            # Calculated isometric direction targets
            self.velocity.x = (dx + dz) * cos_45
            self.velocity.z = (dz - dx) * sin_45
        else:
            self.velocity.x = 0.0
            self.velocity.z = 0.0

        # Calculate intended frame travel speed
        move_step_x = self.velocity.x * self.speed * dt
        move_step_z = self.velocity.z * self.speed * dt

        # 3. Apply Axis-Separated Position Resolution
        if game_map is not None:
            # --- TRY X PLANE MOVEMENT ---
            target_x = self.position.x + move_step_x

            # Change game_map.grid, game_map.tile_size -> game_map
            if not is_colliding_with_map(target_x, self.position.z, self.width, self.depth, game_map):
                self.position.x = target_x

            # --- TRY Z PLANE MOVEMENT ---
            target_z = self.position.z + move_step_z

            # Change game_map.grid, game_map.tile_size -> game_map
            if not is_colliding_with_map(self.position.x, target_z, self.width, self.depth, game_map):
                self.position.z = target_z
        else:
            # Fallback if no map is present (unrestricted movement)
            self.position.x += move_step_x
            self.position.z += move_step_z

    def render(self):
        """Draws our wizard character model into the world."""
        # Shift the rendering anchor so the cylinder's bottom sits perfectly flat on the grid floor
        render_pos = pr.Vector3(self.position.x, self.position.y + (self.height / 2.0), self.position.z)
        radius = self.width / 2.0

        pr.draw_cylinder(render_pos, radius, radius, self.height, 16, pr.BLUE)
        pr.draw_cylinder_wires(render_pos, radius, radius, self.height, 16, pr.DARKBLUE)
