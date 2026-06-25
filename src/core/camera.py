import pyray as pr


class IsometricCamera:
    def __init__(self):
        # 1. Instantiate the Camera3D struct cleanly using pyray
        self.cam = pr.Camera3D()

        # 2. Hardcode the initial isometric offset position
        self.cam.position = pr.Vector3(20.0, 25.0, 25.0)

        # 3. Point the camera exactly at the world origin (0, 0, 0)
        self.cam.target = pr.Vector3(0.0, 0.0, 0.0)

        # 4. Define world "Up" direction (Y-axis points up)
        self.cam.up = pr.Vector3(0.0, 1.0, 0.0)

        # 5. Field of view (FOV) in degrees & projection type
        self.cam.fovy = 30.0
        self.cam.projection = pr.CAMERA_PERSPECTIVE

    def update(self, dt, target_pos, cam_offset=10.0):
        """Dynamically locks the camera's focus target and applies a variable offset."""
        # Lerp factor for smooth glide tracking
        lerp_factor = 10.0 * dt
        if lerp_factor > 1.0: lerp_factor = 1.0

        # Smoothly slide target toward the player position
        self.cam.target.x += (target_pos.x - self.cam.target.x) * lerp_factor
        self.cam.target.y += (target_pos.y - self.cam.target.y) * lerp_factor
        self.cam.target.z += (target_pos.z - self.cam.target.z) * lerp_factor

        # Use the dynamic cam_offset slider value instead of a hardcoded 10.0
        self.cam.position = pr.Vector3(
            self.cam.target.x + cam_offset,
            self.cam.target.y + cam_offset,
            self.cam.target.z + cam_offset
        )
