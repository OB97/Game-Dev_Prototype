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
        self.mesh = None
        self.texture = None
        self.material = None

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

        print(f"[MAP] Generated {vertex_count} vertices, {vertex_count // 3} triangles")

        # 3. Create the mesh (don't use load_model_from_mesh, render it directly)
        self.mesh = pr.Mesh()
        self.mesh.vertexCount = vertex_count
        self.mesh.triangleCount = vertex_count // 3
        self.mesh.vertices = pr.ffi.cast("float *", self._vertices_ref)
        self.mesh.normals = pr.ffi.cast("float *", self._normals_ref)

        print(f"[MAP] Mesh created: vertexCount={self.mesh.vertexCount}, triangleCount={self.mesh.triangleCount}")

        # 4. Upload to GPU
        pr.upload_mesh(pr.ffi.addressof(self.mesh), False)
        print("[MAP] Mesh uploaded to GPU")

        # 5. Create a basic material
        self.material = pr.load_material_default()
        print("[MAP] Material created")

    def render(self, tint_color=pr.WHITE):
        """Render the map with ground mesh and tree collision volumes."""
        # Calculate world offset to center the grid at origin
        offset_x = (self.cols * self.tile_size) / 2.0
        offset_z = (self.rows * self.tile_size) / 2.0

        # DIAGNOSTIC: Draw ground plane
        half_size = (self.cols * self.tile_size) / 2.0
        pr.draw_plane(pr.Vector3(0, -0.01, 0), pr.Vector2(half_size * 2, half_size * 2), pr.LIME)

        # Draw red border
        pr.draw_line_3d(
            pr.Vector3(-half_size, 0.01, -half_size),
            pr.Vector3(half_size, 0.01, -half_size),
            pr.RED
        )
        pr.draw_line_3d(
            pr.Vector3(half_size, 0.01, -half_size),
            pr.Vector3(half_size, 0.01, half_size),
            pr.RED
        )
        pr.draw_line_3d(
            pr.Vector3(half_size, 0.01, half_size),
            pr.Vector3(-half_size, 0.01, half_size),
            pr.RED
        )
        pr.draw_line_3d(
            pr.Vector3(-half_size, 0.01, half_size),
            pr.Vector3(-half_size, 0.01, -half_size),
            pr.RED
        )

        # Render the ground mesh
        if self.mesh is not None and self.material is not None:
            pr.draw_mesh(self.mesh, self.material, pr.Matrix())

        # Draw tree collision volumes as visible brown cubes
        # Offset trees south-west from camera's isometric view
        tree_offset_x = -0.5  # Shift trees west (negative X)
        tree_offset_z = 0.5  # Shift trees south (positive Z)

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 1:  # Tree tile
                    # Convert grid coordinates to world coordinates
                    x = (c * self.tile_size) - offset_x + (self.tile_size / 2.0) + tree_offset_x
                    z = (r * self.tile_size) - offset_z + (self.tile_size / 2.0) + tree_offset_z

                    # Draw a brown cube for the tree
                    tree_pos = pr.Vector3(x, self.tile_size / 2.0, z)
                    pr.draw_cube(tree_pos, self.tile_size, self.tile_size, self.tile_size, pr.Color(101, 67, 33, 255))
                    pr.draw_cube_wires(tree_pos, self.tile_size, self.tile_size, self.tile_size, pr.DARKBROWN)
