import random
import pyray as pr
import ctypes


class GameMap:
    def __init__(self, cols=24, rows=24, tree_density=0.12):
        self.cols = cols
        self.rows = rows
        self.tree_density = tree_density
        self.tile_size = 2.0
        self.grid = []
        self.model = None
        self.texture = None

        self._vertices_ref = None
        self._normals_ref = None
        self._texcoords_ref = None

        self.generate_forest()

    def generate_forest(self):
        self.grid = []
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                is_center = (abs(c - self.cols // 2) <= 1 and abs(r - self.rows // 2) <= 1)
                if not is_center and random.random() < self.tree_density:
                    row_data.append(1)
                else:
                    row_data.append(0)
            self.grid.append(row_data)

        self._bake_map_mesh()

    def _bake_map_mesh(self):
        """Generates and uploads mesh data for the grid, centered at origin."""
        vertices = []
        normals = []

        # Calculate world offset to center the grid at origin
        offset_x = (self.cols * self.tile_size) / 2.0
        offset_z = (self.rows * self.tile_size) / 2.0

        # 1. Generate vertices for the grid (each tile is 2 triangles)
        for r in range(self.rows):
            for c in range(self.cols):
                # Generate positions centered around origin
                x = (c * self.tile_size) - offset_x
                z = (r * self.tile_size) - offset_z

                # Triangle 1 (CCW when viewed from above)
                vertices.extend([
                    x, 0, z,
                    x + self.tile_size, 0, z,
                    x, 0, z + self.tile_size
                ])
                # All vertices point upward (normal = Y-up)
                normals.extend([0, 1, 0, 0, 1, 0, 0, 1, 0])

                # Triangle 2 (CCW when viewed from above)
                vertices.extend([
                    x + self.tile_size, 0, z,
                    x + self.tile_size, 0, z + self.tile_size,
                    x, 0, z + self.tile_size
                ])
                # All vertices point upward
                normals.extend([0, 1, 0, 0, 1, 0, 0, 1, 0])

        # 2. Convert to C arrays (anchored to self to prevent GC)
        vertex_count = len(vertices) // 3
        self._vertices_ref = pr.ffi.new("float[]", vertices)
        self._normals_ref = pr.ffi.new("float[]", normals)

        # 3. Create the mesh
        new_mesh = pr.Mesh()
        new_mesh.vertexCount = vertex_count
        new_mesh.triangleCount = vertex_count // 3
        new_mesh.vertices = pr.ffi.cast("float *", self._vertices_ref)
        new_mesh.normals = pr.ffi.cast("float *", self._normals_ref)

        # 4. Upload to GPU
        pr.upload_mesh(pr.ffi.addressof(new_mesh), False)

        # 5. Create or swap models
        if self.model is not None:
            pr.unload_model(self.model)

        self.model = pr.load_model_from_mesh(new_mesh)

        # Load texture once
        if self.texture is not None:
            pr.unload_texture(self.texture)

        grass_image = pr.gen_image_color(1, 1, pr.Color(110, 140, 105, 255))
        self.texture = pr.load_texture_from_image(grass_image)
        pr.unload_image(grass_image)

        # Apply texture to material
        pr.set_material_texture(self.model.materials[0], pr.MATERIAL_MAP_DIFFUSE, self.texture)

    def render(self, tint_color=pr.WHITE):
        """Render the map with proper lighting."""
        if self.model is not None:
            pr.draw_model(self.model, pr.Vector3(0, 0, 0), 1.0, tint_color)
