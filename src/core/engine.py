import pyray as pr
from src.core.camera import IsometricCamera
from src.entities.player import Player
from src.world.map import GameMap


class Engine:
    def __init__(self, width=1024, height=768, title="Wizard Isometric Prototype"):
        pr.init_window(width, height, title)
        pr.set_target_fps(60)

        self.camera_system = IsometricCamera()
        self.player = Player(x=0.0, y=0.0, z=0.0)

        # Instantiate our new procedural Forest Map
        self.game_map = GameMap(cols=24, rows=24, tree_density=0.12)

        self.entities = [self.player]

        # Sandbox parameters
        self.camera_offset = 14.0
        self.panel_expanded = True

        # New Sandbox Debug flags mapped to our future Dev Suite hooks
        self.show_wireframes = False
        self.god_mode = False

        self.is_running = True

    def run(self):
        while not pr.window_should_close():
            if not self.is_running:
                break
            self._update()
            self._render()
        self.close()

    def _update(self):
        """Update game state, physics, and input systems."""
        dt = pr.get_frame_time()

        # Pass the procedural map instance down so the player can calculate tree boundaries
        self.player.update(dt, self.game_map)

        self.camera_system.update(dt, self.player.position, self.camera_offset)

    def _render(self):
        pr.begin_drawing()
        pr.clear_background(pr.Color(15, 15, 20, 255))  # Dark void backdrop

        # 3D World Space context
        pr.begin_mode_3d(self.camera_system.cam)

        # Render our map level layouts
        self.game_map.render()

        # Draw optional wireframes grid if debugging flag is true
        if self.show_wireframes:
            pr.draw_grid(40, 1.0)

        for entity in self.entities:
            entity.render()

        pr.end_mode_3d()

        # =====================================================================
        # 2D DEV SANDBOX PANEL OVERLAY (Screen Space UI)
        # =====================================================================
        panel_x, panel_y = 10, 10
        slider_w, slider_h = 200, 12
        mouse_pos = pr.get_mouse_position()

        if self.panel_expanded:
            panel_w, panel_h = 280, 290  # Expanded height for new dev suites
            btn_text = "[-] Hide Panel"
        else:
            panel_w, panel_h = 160, 40
            btn_text = "[+] Dev Panel"

        pr.draw_rectangle(panel_x, panel_y, panel_w, panel_h, pr.fade(pr.BLACK, 0.85))
        pr.draw_rectangle_lines(panel_x, panel_y, panel_w, panel_h, pr.DARKGRAY)

        # Toggle Button
        btn_x, btn_y, btn_w, btn_h = panel_x + 15, panel_y + 10, 110, 20
        is_hovered = (btn_x <= mouse_pos.x <= btn_x + btn_w and btn_y <= mouse_pos.y <= btn_y + btn_h)
        pr.draw_text(btn_text, btn_x, btn_y, 14, pr.GREEN if is_hovered else pr.DARKGREEN)

        if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT) and is_hovered:
            self.panel_expanded = not self.panel_expanded

        # Draw nested adjustments
        if self.panel_expanded:
            pr.draw_fps(panel_x + 160, panel_y + 10)

            # --- SLIDER 1: PLAYER SPEED ---
            pr.draw_text(f"Player Speed: {self.player.speed:.1f}", panel_x + 15, panel_y + 45, 12, pr.WHITE)
            p_slider_x, p_slider_y = panel_x + 15, panel_y + 60
            pr.draw_rectangle(p_slider_x, p_slider_y, slider_w, slider_h, pr.GRAY)

            # --- SLIDER 2: CAMERA DISTANCE ---
            pr.draw_text(f"Camera Distance: {self.camera_offset:.1f}", panel_x + 15, panel_y + 85, 12, pr.WHITE)
            c_slider_x, c_slider_y = panel_x + 15, panel_y + 100
            pr.draw_rectangle(c_slider_x, c_slider_y, slider_w, slider_h, pr.GRAY)

            # Continuous Drag Handling
            if pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT):
                if p_slider_x <= mouse_pos.x <= p_slider_x + slider_w and p_slider_y <= mouse_pos.y <= p_slider_y + slider_h:
                    self.player.speed = 1.0 + (((mouse_pos.x - p_slider_x) / slider_w) * 19.0)
                if c_slider_x <= mouse_pos.x <= c_slider_x + slider_w and c_slider_y <= mouse_pos.y <= c_slider_y + slider_h:
                    self.camera_offset = 4.0 + (((mouse_pos.x - c_slider_x) / slider_w) * 26.0)

            # Draw Knob Handles
            p_knob_x = int(p_slider_x + (((self.player.speed - 1.0) / 19.0) * slider_w))
            pr.draw_circle(p_knob_x, p_slider_y + 6, 6, pr.SKYBLUE)
            c_knob_x = int(c_slider_x + (((self.camera_offset - 4.0) / 26.0) * slider_w))
            pr.draw_circle(c_knob_x, c_slider_y + 6, 6, pr.LIME)

            # --- WORLD GEN & CHEATS SECTION ---
            pr.draw_line(panel_x + 15, panel_y + 130, panel_x + 265, panel_y + 130, pr.DARKGRAY)

            # Action Button 1: Re-generate Forest
            regen_x, regen_y, regen_w, regen_h = panel_x + 15, panel_y + 145, 150, 22
            h_regen = (regen_x <= mouse_pos.x <= regen_x + regen_w and regen_y <= mouse_pos.y <= regen_y + regen_h)
            pr.draw_rectangle(regen_x, regen_y, regen_w, regen_h, pr.DARKBLUE if h_regen else pr.BLUE)
            pr.draw_text("Regen Forest Map", regen_x + 10, regen_y + 5, 12, pr.WHITE)

            # Action Button 2: Toggle Wireframe Debug lines
            wire_x, wire_y, wire_w, wire_h = panel_x + 15, panel_y + 175, 150, 22
            h_wire = (wire_x <= mouse_pos.x <= wire_x + wire_w and wire_y <= mouse_pos.y <= wire_y + wire_h)
            wire_color = pr.GREEN if self.show_wireframes else pr.MAROON
            pr.draw_rectangle(wire_x, wire_y, wire_w, wire_h, pr.fade(wire_color, 0.8) if h_wire else wire_color)
            pr.draw_text(f"Grid Lines: {'ON' if self.show_wireframes else 'OFF'}", wire_x + 10, wire_y + 5, 12,
                         pr.WHITE)

            # Action Button 3: God Mode Placeholder
            god_x, god_y, god_w, god_h = panel_x + 15, panel_y + 205, 150, 22
            h_god = (god_x <= mouse_pos.x <= god_x + god_w and god_y <= mouse_pos.y <= god_y + god_w)
            god_color = pr.GOLD if self.god_mode else pr.DARKGRAY
            pr.draw_rectangle(god_x, god_y, god_w, god_h, god_color)
            pr.draw_text(f"God Mode: {'ON' if self.god_mode else 'OFF'}", god_x + 10, god_y + 5, 12,
                         pr.BLACK if self.god_mode else pr.WHITE)

            # Handle Button Pressed Events
            if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
                if h_regen:
                    self.game_map.generate_forest()
                if h_wire:
                    self.show_wireframes = not self.show_wireframes
                if h_god:
                    self.god_mode = not self.god_mode

            # Position Coordinates Footer info
            pos_str = f"XYZ: ({self.player.position.x:.1f}, {self.player.position.y:.1f}, {self.player.position.z:.1f})"
            pr.draw_text(pos_str, panel_x + 15, panel_y + 260, 12, pr.LIGHTGRAY)

        pr.end_drawing()

    def close(self):
        pr.close_window()
