#!/usr/bin/python3
import sys
import dearpygui.dearpygui as gui
from pathlib import Path
import numpy as np
from v360 import FFXController

"""
TODO: merge windows
    -> big table as layout
    -> get stick center position programatically
"""

EPS = 1e-5


def redistribute_rgb(color_rgb):
    r, g, b = color_rgb
    threshold = 255.999
    m = max(r, g, b)
    if m <= threshold:
        return int(r), int(g), int(b)
    total = r + g + b
    if total >= 3 * threshold:
        return int(threshold), int(threshold), int(threshold)
    x = (3 * threshold - total) / (3 * m - total)
    gray = threshold - x * m
    return [int(gray + x * r), int(gray + x * g), int(gray + x * b)]


def lighten(c, a):
    return redistribute_rgb([a*c[0], a*c[1], a*c[2]])


class MainWindow:
    def __init__(self):
        self.controller = FFXController()
        self.size = 150
        self.center = [self.size/2, self.size/2]
        self.thickness = 5
        self.outer_radius = 0.75*(self.size/2 - self.thickness / 2)
        self.inner_radius = self.size/20
        self.color = [128, 128, 128]
        self.position = self.center

    def update_stick(self):
        # Translate w.r.t center (neutral) position
        pos = np.array(self.position) - self.size / 2
        # Cap position
        norm = np.linalg.norm(pos)
        max_norm = self.outer_radius - self.inner_radius - self.thickness
        if norm > max_norm:
            pos = max_norm * pos/norm

        # Update controller
        norm = np.linalg.norm(pos)
        ctl_pos = pos / norm if norm > EPS else np.zeros(2)
        self.controller.set_movement(*ctl_pos)

        gui.apply_transform(
            "__stick_node", gui.create_translation_matrix(list(pos)))

    def on_mouse_down(self, sender, user_data):
        if gui.is_item_hovered('__canvas'):
            self.position = gui.get_drawing_mouse_pos()
            self.update_stick()

    def on_mouse_release(self, sender, user_data):
        self.position = self.center
        self.update_stick()

    def button_pressed(self, sender, app_data, user_data):
        key = user_data
        self.controller.set_value(key, 1)

    def render_stick(self):
        with gui.drawlist(width=self.size, height=self.size, tag="__canvas"):
            # Background circle
            gui.draw_circle(center=self.center,
                            radius=self.outer_radius, color=self.color, thickness=self.thickness)
            # Movable stick
            with gui.draw_node(tag="__stick_node"):
                gui.draw_circle(center=self.position,
                                radius=self.inner_radius, fill=self.color)

    def render_right_buttons(self):
        colors_rgb = [
            [254, 187, 40],
            [36,  103, 167],
            [200, 50,  37],
            [152, 180, 70]
        ]
        for i, color in enumerate(colors_rgb):
            with gui.theme(tag=f"__btn_theme_{i}"):
                with gui.theme_component(gui.mvButton):
                    gui.add_theme_color(gui.mvThemeCol_Text, [0, 0, 0])
                    gui.add_theme_color(gui.mvThemeCol_Button, color)
                    gui.add_theme_color(
                        gui.mvThemeCol_ButtonActive, lighten(color, 1.5))
                    gui.add_theme_color(
                        gui.mvThemeCol_ButtonHovered, lighten(color, 1.3))
                    gui.add_theme_style(gui.mvStyleVar_FrameRounding, 10)
                    gui.add_theme_style(gui.mvStyleVar_FramePadding, 3, 3)

        with gui.table(header_row=False):
            gui.add_table_column()
            gui.add_table_column()
            gui.add_table_column()

            with gui.table_row():
                gui.add_spacer()
                gui.add_button(
                    label=" Y ", callback=self.button_pressed, user_data="BtnY")
                gui.bind_item_theme(gui.last_item(), "__btn_theme_0")
                gui.add_spacer()

            with gui.table_row():
                gui.add_button(
                    label=" X ", callback=self.button_pressed, user_data="BtnX")
                gui.bind_item_theme(gui.last_item(), "__btn_theme_1")
                gui.add_spacer()
                gui.add_button(
                    label=" B ", callback=self.button_pressed, user_data="BtnB")
                gui.bind_item_theme(gui.last_item(), "__btn_theme_2")

            with gui.table_row():
                gui.add_spacer()
                gui.add_button(
                    label=" A ", callback=self.button_pressed, user_data="BtnA")
                gui.bind_item_theme(gui.last_item(), "__btn_theme_3")
                gui.add_spacer()

    def render(self):
        with gui.handler_registry():
            gui.add_mouse_drag_handler(callback=self.on_mouse_down)
            gui.add_mouse_click_handler(callback=self.on_mouse_down)
            gui.add_mouse_release_handler(callback=self.on_mouse_release)

        with gui.window(label="Gamepad", tag="__gamepad_window"):
            with gui.table(header_row=False):
                gui.add_table_column()
                gui.add_table_column()
                with gui.table_row():
                    self.render_stick()
                    self.render_right_buttons()


def main(argv):
    local = Path(__file__).parent
    init_path = local / "gui.ini"
    window = MainWindow()

    gui.create_context()
    gui.configure_app(init_file=init_path, docking=True)
    gui.create_viewport(title="v360 GUI", width=600, height=300)
    gui.setup_dearpygui()

    window.render()

    gui.show_viewport()
    gui.start_dearpygui()
    gui.destroy_context()


if __name__ == '__main__':
    main(sys.argv[1:])
