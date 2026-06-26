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
        self.game_map = GameMap(cols=24, rows=24, tree_density=0.12)
        self.entities = [self.player]

        # Sandbox parameters
        self.camera_offset = 14.0
        self.panel_expanded = True
        self.show_wireframes = False
        self.god_mode = False
        self.is_running = True

        # Day-Night Cycle Parameters
        self.time_of_day = 0.25  # Normalized time parameter (0.0 to 1.0)
        self.sun_speed = 0.02  # Progression delta coefficient

        # Ambient color cycle target values
        self.bg_color = pr.Color(15, 15, 20, 255)
        self.light_tint = pr.WHITE

    def run(self):
        while not pr.window_should_close():
            if not self.is_running:
                break
            self._update()
            self._render()
        self.close()

    def _update(self):
        """Updates physics properties, cycle engines, and processes UI events state elements."""
        dt = pr.get_frame_time()

        # Run input parsing safely prior to triggering rendering sequences
        self._handle_ui_input()

        # Advance clock values based on the slider metrics
        self.time_of_day = (self.time_of_day + self.sun_speed * dt) % 1.0
        self._update_environment_lighting()

        self.player.update(dt, self.game_map)
        self.camera_system.update(dt, self.player.position, self.camera_offset)

    def _update_environment_lighting(self):
        """Computes current ambient color values and visual lighting state configurations."""
        # 0.0 & 1.0 = Midnight, 0.25 = Morning, 0.5 = Noon, 0.75 = Sunset
        t = self.time_of_day

        # Define color stops across key timeframes
        midnight_bg = pr.Color(10, 10, 18, 255)
        noon_bg = pr.Color(45, 75, 115, 255)
        sunset_bg = pr.Color(60, 35, 45, 255)

        midnight_tint = pr.Color(60, 60, 90, 255)
        noon_tint = pr.Color(255, 255, 240, 255)
        sunset_tint = pr.Color(240, 140, 90, 255)

        if t < 0.25:  # Late Night leading up into Sunrise
            factor = t / 0.25
            self.bg_color = self._color_lerp(midnight_bg, noon_bg, factor)
            self.light_tint = self._color_lerp(midnight_tint, noon_tint, factor)
        elif t < 0.5:  # Morning up through high Noon
            factor = (t - 0.25) / 0.25
            self.bg_color = noon_bg
            self.light_tint = noon_tint
        elif t < 0.75:  # Afternoon dropping off toward Sunset
            factor = (t - 0.5) / 0.25
            self.bg_color = self._color_lerp(noon_bg, sunset_bg, factor)
            self.light_tint = self._color_lerp(noon_tint, sunset_tint, factor)
        else:  # Sunset fading deep back into Twilight
            factor = (t - 0.75) / 0.25
            self.bg_color = self._color_lerp(sunset_bg, midnight_bg, factor)
            self.light_tint = self._color_lerp(sunset_tint, midnight_tint, factor)

    def _color_lerp(self, c1, c2, factor):
        """Helper to linearly interpolate transition steps between two primary Color items."""
        factor = max(0.0, min(1.0, factor))
        return pr.Color(
            int(c1.r + (c2.r - c1.r) * factor),
            int(c1.g + (c2.g - c1.g) * factor),
            int(c1.b + (c2.b - c1.b) * factor),
            255
        )

    def _handle_ui_input(self):
        """Processes logic events, handles UI mouse dragging, and updates state."""
        mouse_pos = pr.get_mouse_position()
        panel_x, panel_y = 10, 10
        slider_w, slider_h = 200, 12

        if self.panel_expanded:
            panel_w, panel_h = 280, 350  # Expanded space to host Day/Night options cleanly
        else:
            panel_w, panel_h = 160, 40

        # Hover configurations
        btn_x, btn_y, btn_w, btn_h = panel_x + 15, panel_y + 10, 110, 20
        self.is_panel_btn_hovered = (btn_x <= mouse_pos.x <= btn_x + btn_w and btn_y <= mouse_pos.y <= btn_y + btn_h)

        # Toggle Main Panel Expand state
        if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT) and self.is_panel_btn_hovered:
            self.panel_expanded = not self.panel_expanded
            return

        if self.panel_expanded:
            p_slider_x, p_slider_y = panel_x + 15, panel_y + 60
            c_slider_x, c_slider_y = panel_x + 15, panel_y + 100
            t_slider_x, t_slider_y = panel_x + 15, panel_y + 140

            # Active Action element configurations
            regen_x, regen_y, regen_w, regen_h = panel_x + 15, panel_y + 185, 150, 22
            wire_x, wire_y, wire_w, wire_h = panel_x + 15, panel_y + 215, 150, 22
            god_x, god_y, god_w, god_h = panel_x + 15, panel_y + 245, 150, 22

            self.h_regen = (regen_x <= mouse_pos.x <= regen_x + regen_w and regen_y <= mouse_pos.y <= regen_y + regen_h)
            self.h_wire = (wire_x <= mouse_pos.x <= wire_x + wire_w and wire_y <= mouse_pos.y <= wire_y + wire_h)
            self.h_god = (god_x <= mouse_pos.x <= god_x + god_w and god_y <= mouse_pos.y <= god_y + god_h)

            # Continuous Drag UI Handling
            if pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT):
                # Player Speed Slider
                if p_slider_x <= mouse_pos.x <= p_slider_x + slider_w and p_slider_y <= mouse_pos.y <= p_slider_y + slider_h:
                    self.player.speed = 1.0 + (((mouse_pos.x - p_slider_x) / slider_w) * 19.0)
                # Camera Distance Slider
                elif c_slider_x <= mouse_pos.x <= c_slider_x + slider_w and c_slider_y <= mouse_pos.y <= c_slider_y + slider_h:
                    self.camera_offset = 4.0 + (((mouse_pos.x - c_slider_x) / slider_w) * 26.0)
                # Day-Night Progression Cycle Speed Slider
                elif t_slider_x <= mouse_pos.x <= t_slider_x + slider_w and t_slider_y <= mouse_pos.y <= t_slider_y + slider_h:
                    self.sun_speed = 0.0 + (((mouse_pos.x - t_slider_x) / slider_w) * 0.1)

            # Concrete Click Actions Selection Processing
            if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
                if self.h_regen:
                    self.game_map.generate_forest()
                elif self.h_wire:
                    self.show_wireframes = not self.show_wireframes
                elif self.h_god:
                    self.god_mode = not self.god_mode

    def _render(self):
        """Pure, declarative execution window processing. No mutations are performed here."""
        pr.begin_drawing()
        pr.clear_background(self.bg_color)

        # 3D Render Context Pass
        pr.begin_mode_3d(self.camera_system.cam)

        # Draw map injecting the processed day/night color shading parameters
        self.game_map.render(tint_color=self.light_tint)

        if self.show_wireframes:
            pr.draw_grid(40, 1.0)

        for entity in self.entities:
            entity.render()

        pr.end_mode_3d()

        # =====================================================================
        # 2D DEV SANDBOX PANEL OVERLAY (Screen Space Declarative UI)
        # =====================================================================
        panel_x, panel_y = 10, 10
        slider_w, slider_h = 200, 12

        if self.panel_expanded:
            panel_w, panel_h = 280, 330
            btn_text = "[-] Hide Panel"
        else:
            panel_w, panel_h = 160, 40
            btn_text = "[+] Dev Panel"

        pr.draw_rectangle(panel_x, panel_y, panel_w, panel_h, pr.fade(pr.BLACK, 0.85))
        pr.draw_rectangle_lines(panel_x, panel_y, panel_w, panel_h, pr.DARKGRAY)

        # Toggle Visibility Trigger Button element
        btn_x, btn_y = panel_x + 15, panel_y + 10
        pr.draw_text(btn_text, btn_x, btn_y, 14, pr.GREEN if self.is_panel_btn_hovered else pr.DARKGREEN)

        if self.panel_expanded:
            pr.draw_fps(panel_x + 160, panel_y + 10)

            # --- SLIDER 1: PLAYER SPEED ---
            pr.draw_text(f"Player Speed: {self.player.speed:.1f}", panel_x + 15, panel_y + 45, 12, pr.WHITE)
            p_slider_x, p_slider_y = panel_x + 15, panel_y + 60
            pr.draw_rectangle(p_slider_x, p_slider_y, slider_w, slider_h, pr.GRAY)
            p_knob_x = int(p_slider_x + (((self.player.speed - 1.0) / 19.0) * slider_w))
            pr.draw_circle(p_knob_x, p_slider_y + 6, 6, pr.SKYBLUE)

            # --- SLIDER 2: CAMERA DISTANCE ---
            pr.draw_text(f"Camera Distance: {self.camera_offset:.1f}", panel_x + 15, panel_y + 85, 12, pr.WHITE)
            c_slider_x, c_slider_y = panel_x + 15, panel_y + 100
            pr.draw_rectangle(c_slider_x, c_slider_y, slider_w, slider_h, pr.GRAY)
            c_knob_x = int(c_slider_x + (((self.camera_offset - 4.0) / 26.0) * slider_w))
            pr.draw_circle(c_knob_x, c_slider_y + 6, 6, pr.LIME)

            # --- SLIDER 3: SUN MOVEMENT SPEED ---
            pr.draw_text(f"Sun Speed: {self.sun_speed * 100:.1f}%", panel_x + 15, panel_y + 125, 12, pr.WHITE)
            t_slider_x, t_slider_y = panel_x + 15, panel_y + 140
            pr.draw_rectangle(t_slider_x, t_slider_y, slider_w, slider_h, pr.GRAY)
            t_knob_x = int(t_slider_x + ((self.sun_speed / 0.1) * slider_w))
            pr.draw_circle(t_knob_x, t_slider_y + 6, 6, pr.GOLD)

            # --- WORLD GEN & CHEATS ---
            pr.draw_line(panel_x + 15, panel_y + 170, panel_x + 265, panel_y + 170, pr.DARKGRAY)

            # Action Button 1: Regenerate Map
            regen_x, regen_y = panel_x + 15, panel_y + 185
            pr.draw_rectangle(regen_x, regen_y, 150, 22, pr.DARKBLUE if self.h_regen else pr.BLUE)
            pr.draw_text("Regen Forest Map", regen_x + 10, regen_y + 5, 12, pr.WHITE)

            # Action Button 2: Toggle Wireframe Debug lines
            wire_x, wire_y = panel_x + 15, panel_y + 215
            wire_color = pr.GREEN if self.show_wireframes else pr.MAROON
            pr.draw_rectangle(wire_x, wire_y, 150, 22, pr.fade(wire_color, 0.8) if self.h_wire else wire_color)
            pr.draw_text(f"Grid Lines: {'ON' if self.show_wireframes else 'OFF'}", wire_x + 10, wire_y + 5, 12,
                         pr.WHITE)

            # Action Button 3: God Mode
            god_x, god_y = panel_x + 15, panel_y + 245
            god_color = pr.GOLD if self.god_mode else pr.DARKGRAY
            pr.draw_rectangle(god_x, god_y, 150, 22, god_color)
            pr.draw_text(f"God Mode: {'ON' if self.god_mode else 'OFF'}", god_x + 10, god_y + 5, 12,
                         pr.BLACK if self.god_mode else pr.WHITE)

            # Current Coordinate Display / Universal Status Clock Footer
            pos_str = f"XYZ: ({self.player.position.x:.1f}, {self.player.position.y:.1f}, {self.player.position.z:.1f})"
            time_str = f"Time Phase Ratio: {self.time_of_day:.2f}"
            pr.draw_text(pos_str, panel_x + 15, panel_y + 285, 12, pr.LIGHTGRAY)
            pr.draw_text(time_str, panel_x + 15, panel_y + 305, 12, pr.GOLD)

        pr.end_drawing()

    def close(self):
        # Cleanup instantiated models cleanly before window termination safely exits system
        if self.game_map.model is not None:
            pr.unload_model(self.game_map.model)
        pr.close_window()
