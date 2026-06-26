import pyray as pr


class IsometricCamera:
    def __init__(self):
        # 1. Instantiate the Camera3D struct cleanly using pyray
        self.cam = pr.Camera3D()

        # 2. Position camera for isometric view of ground plane
        # For a flat map at Y=0, position camera lower and offset equally in X and Z
        self.cam.position = pr.Vector3(15.0, 12.0, 15.0)

        # 3. Point the camera at ground level (Y slightly above 0 for better visibility)
        self.cam.target = pr.Vector3(0.0, 0.5, 0.0)

        # 4. Define world "Up" direction (Y-axis points up)
        self.cam.up = pr.Vector3(0.0, 1.0, 0.0)

        # 5. Field of view (FOV) in degrees & projection type
        self.cam.fovy = 45.0
        self.cam.projection = pr.CAMERA_PERSPECTIVE

    def update(self, dt, target_pos, cam_offset=10.0):
        """Dynamically locks the camera's focus target and applies a variable offset."""
        # Lerp factor for smooth glide tracking
        lerp_factor = 10.0 * dt
        if lerp_factor > 1.0: lerp_factor = 1.0

        # Smoothly slide target toward the player position (keep Y at ground + offset)
        self.cam.target.x += (target_pos.x - self.cam.target.x) * lerp_factor
        self.cam.target.y = 0.5  # Keep focused slightly above ground
        self.cam.target.z += (target_pos.z - self.cam.target.z) * lerp_factor

        # Use the dynamic cam_offset slider value for isometric distance
        # Position camera equally offset in X, Y, and Z for isometric view
        self.cam.position = pr.Vector3(
            self.cam.target.x + cam_offset,
            cam_offset,  # Height above ground (use offset value)
            self.cam.target.z + cam_offset
        )
