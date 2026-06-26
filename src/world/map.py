import random
import pyray as pr


class GameMap:
    def __init__(self, cols=20, rows=20, tree_density=0.15):
        self.cols = cols
        self.rows = rows
        self.tree_density = tree_density
        self.tile_size = 2.0
        self.grid = []
        self.model = None

        # Keep references to raw memory arrays to prevent Python's Garbage Collector from deleting them
        self._vertices_ref = None
        self._normals_ref = None
        self._texcoords_ref = None

        self.generate_forest()

    def generate_forest(self):
        """Randomizes the layout grid array and prompts a 3D geometry rebuild pass."""
        # --- FIXED SEGFAULT & ATTRIBUTE ERROR SAFETY CHECK ---
        if hasattr(self, 'model') and self.model is not None:
            # Check if it points to an active Raylib structure before unloading
            try:
                if hasattr(self.model, 'id') and self.model.id != 0:
                    pr.unload_model(self.model)
            except AttributeError:
                pass  # Fallback safety if the struct isn't fully bound yet
        # -----------------------------------------------------

        # Clear/create the map grid structure
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Populate random obstacle trees
        for row in range(self.rows):
            for col in range(self.cols):
                # Leave a 3x3 clearing right in the center for the player to spawn safely
                center_r, center_c = self.rows // 2, self.cols // 2
                if abs(row - center_r) <= 1 and abs(col - center_c) <= 1:
                    continue

                if random.random() < self.tree_density:
                    self.grid[row][col] = 1

        # Force immediate structural bake update to build the 3D visual object
        self._bake_map_mesh()

    def _bake_map_mesh(self):
        """Combines all individual tree geometries into one high-performance composite mesh."""
        # --- CRITICAL FIX: Cleanly unload existing model from GPU memory before re-baking ---
        if hasattr(self, 'model') and self.model is not None:
            pr.unload_model(self.model)
        # ----------------------------------------------------------------------------

        offset_x = (self.cols * self.tile_size) / 2.0
        offset_z = (self.rows * self.tile_size) / 2.0
        cube_height = 2.0

        # Build a temporary base cube mesh to grab component source layout vectors
        base_cube_mesh = pr.gen_mesh_cube(self.tile_size, cube_height, self.tile_size)

        all_vertices = []
        all_texcoords = []
        all_normals = []

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 1:
                    world_x = (col * self.tile_size) - offset_x + (self.tile_size / 2.0)
                    world_z = (row * self.tile_size) - offset_z + (self.tile_size / 2.0)
                    world_y = cube_height / 2.0

                    for i in range(base_cube_mesh.vertexCount):
                        vx = base_cube_mesh.vertices[i * 3] + world_x
                        vy = base_cube_mesh.vertices[i * 3 + 1] + world_y
                        vz = base_cube_mesh.vertices[i * 3 + 2] + world_z
                        all_vertices.extend([vx, vy, vz])

                        all_normals.extend([
                            base_cube_mesh.normals[i * 3],
                            base_cube_mesh.normals[i * 3 + 1],
                            base_cube_mesh.normals[i * 3 + 2]
                        ])
                        all_texcoords.extend([
                            base_cube_mesh.texcoords[i * 2],
                            base_cube_mesh.texcoords[i * 2 + 1]
                        ])

        pr.unload_mesh(base_cube_mesh)

        if len(all_vertices) == 0:
            fallback_mesh = pr.gen_mesh_cube(0, 0, 0)
            self.model = pr.load_model_from_mesh(fallback_mesh)
            return

        baked_mesh = pr.Mesh()
        baked_mesh.vertexCount = len(all_vertices) // 3
        baked_mesh.triangleCount = baked_mesh.vertexCount // 3

        # CRITICAL FIX: Save allocations to 'self' so Python preserves this memory pool
        self._vertices_ref = pr.ffi.new(f"float[{len(all_vertices)}]", all_vertices)
        self._normals_ref = pr.ffi.new(f"float[{len(all_normals)}]", all_normals)
        self._texcoords_ref = pr.ffi.new(f"float[{len(all_texcoords)}]", all_texcoords)

        # Map saved continuous structures onto raylib pointers
        baked_mesh.vertices = pr.ffi.cast("float *", self._vertices_ref)
        baked_mesh.normals = pr.ffi.cast("float *", self._normals_ref)
        baked_mesh.texcoords = pr.ffi.cast("float *", self._texcoords_ref)

        # Securely upload the combined tree setup directly to graphics memory
        pr.upload_mesh(baked_mesh, False)
        self.model = pr.load_model_from_mesh(baked_mesh)

    def render(self, tint_color=pr.WHITE):
        """Draws the entire baked forest map layout inside a single GPU instruction execution."""
        if self.model is not None:
            self.model.materials[0].maps[pr.MATERIAL_MAP_DIFFUSE].color = pr.Color(110, 140, 105, 255)
            pr.draw_model(self.model, pr.Vector3(0, 0, 0), 1.0, tint_color)
