import pyray as pr


class BaseEntity:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        # Position in 3D world coordinates
        self.position = pr.Vector3(x, y, z)

        # Velocity vector for movement tracking
        self.velocity = pr.Vector3(0.0, 0.0, 0.0)

        # Speed multiplier
        self.speed = 5.0

    def update(self, dt):
        """
        Calculates position adjustments over time.
        Overridden by child classes for custom behavior.
        """
        # Apply velocity scaled by delta time for framerate-independent movement
        self.position.x += self.velocity.x * self.speed * dt
        self.position.y += self.velocity.y * self.speed * dt
        self.position.z += self.velocity.z * self.speed * dt

    def render(self):
        """
        Draws the entity in the 3D space.
        Must be overridden by child classes (Player, Enemy, etc.).
        """
        pass
