#!/usr/bin/python3
import sys
import dearpygui.dearpygui as dpg
from pathlib import Path
import numpy as np
from v360 import FFXController

"""

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
    def __init__(self, width, height):
        self.controller = FFXController()
        self.width = width
        self.height = height
        self.size = 150
        self.center = [self.size/2, self.size/2]
        self.thickness = 5
        self.outer_radius = 0.75*(self.size/2 - self.thickness / 2)
        self.inner_radius = self.size/20
        self.color = [128, 128, 128]
        self.position = self.center
        self.window_options = {
            "no_resize": True, "no_scrollbar": True, "no_title_bar": True, "no_move": True}

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

        dpg.apply_transform(
            "__stick_node", dpg.create_translation_matrix(list(pos)))

    def on_mouse_down(self, sender, user_data):
        if dpg.is_item_hovered('__stick_canvas'):
            self.position = dpg.get_drawing_mouse_pos()
            self.update_stick()

    def on_mouse_release(self, sender, user_data):
        self.position = self.center
        self.update_stick()

    def button_down(self, sender, app_data, user_data):
        key, value = dpg.get_item_user_data(app_data)
        self.controller.set_value(key, value)

    def button_release(self, sender, app_data, user_data):
        key, value = dpg.get_item_user_data(app_data)
        self.controller.set_value(key, 0)

    def setup_themes(self):
        colors_rgb = [
            [254, 187, 40],
            [36,  103, 167],
            [200, 50,  37],
            [152, 180, 70]
        ]
        for i, color in enumerate(colors_rgb):
            with dpg.theme(tag=f"__btn_theme_{i}"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_Button, color)
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonActive, lighten(color, 1.5))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonHovered, lighten(color, 1.3))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3)

    def render_stick(self):
        with dpg.drawlist(width=self.size, height=self.size, tag="__stick_canvas"):
            # Background circle
            dpg.draw_circle(center=self.center,
                            radius=self.outer_radius, color=self.color, thickness=self.thickness)
            # Movable stick
            with dpg.draw_node(tag="__stick_node"):
                dpg.draw_circle(center=self.position,
                                radius=self.inner_radius, fill=self.color)

    def render_right_buttons(self):
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()

            with dpg.table_row():
                dpg.add_spacer()
                dpg.add_button(label=" Y ", tag="__btn_Y",
                               user_data=("BtnY", 1))
                dpg.bind_item_theme(dpg.last_item(), "__btn_theme_0")
                dpg.add_spacer()

            with dpg.table_row():
                dpg.add_button(
                    label=" X ", tag="__btn_X", user_data=("BtnX", 1))
                dpg.bind_item_theme(dpg.last_item(), "__btn_theme_1")
                dpg.add_spacer()
                dpg.add_button(
                    label=" B ", tag="__btn_B", user_data=("BtnB", 1))
                dpg.bind_item_theme(dpg.last_item(), "__btn_theme_2")

            with dpg.table_row():
                dpg.add_spacer()
                dpg.add_button(
                    label=" A ", tag="__btn_A", user_data=("BtnA", 1))
                dpg.bind_item_theme(dpg.last_item(), "__btn_theme_3")
                dpg.add_spacer()

    def render_dpad(self):
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()

            with dpg.table_row():
                dpg.add_spacer()
                dpg.add_button(arrow=True, direction=dpg.mvDir_Up,
                               tag="__btn_dpad_u", user_data=("Dpad", 1))
                dpg.add_spacer()

            with dpg.table_row():
                dpg.add_button(arrow=True, direction=dpg.mvDir_Left,
                               tag="__btn_dpad_l", user_data=("Dpad", 4))
                dpg.add_spacer()
                dpg.add_button(arrow=True, direction=dpg.mvDir_Right,
                               tag="__btn_dpad_r", user_data=("Dpad", 8))

            with dpg.table_row():
                dpg.add_spacer()
                dpg.add_button(arrow=True, direction=dpg.mvDir_Down,
                               tag="__btn_dpad_d", user_data=("Dpad", 2))
                dpg.add_spacer()

    def render(self):
        with dpg.handler_registry():
            dpg.add_mouse_drag_handler(callback=self.on_mouse_down)
            dpg.add_mouse_click_handler(callback=self.on_mouse_down)
            dpg.add_mouse_release_handler(callback=self.on_mouse_release)

        with dpg.item_handler_registry(tag="__btn_handler"):
            dpg.add_item_activated_handler(callback=self.button_down)
            dpg.add_item_deactivated_handler(callback=self.button_release)

        with dpg.window(label="Gamepad", tag="__gamepad_window", width=self.width, height=self.height, **self.window_options):
            self.setup_themes()
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_button(
                        label="Shoulder L", tag="__btn_sh_l", user_data=("BtnShoulderL", 1), width=300)
                    dpg.add_button(
                        label="Shoulder R", tag="__btn_sh_r", user_data=("BtnShoulderR", 1), width=300)
                with dpg.table_row():
                    dpg.add_button(
                        label="Trigger L", tag="__btn_tr_l", user_data=("TriggerL", 1), width=300)
                    dpg.add_button(
                        label="Trigger R", tag="__btn_tr_r", user_data=("TriggerR", 1), width=300)

            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    with dpg.table(header_row=False):
                        dpg.add_table_column()
                        dpg.add_table_column()

                        with dpg.table_row():
                            dpg.add_button(
                                label="Back", tag="__btn_back", user_data=("BtnBack", 1), width=150)
                            dpg.add_button(
                                label="Start", tag="__btn_start", user_data=("BtnStart", 1), width=150)

                        with dpg.table_row():
                            with dpg.group():
                                dpg.add_spacer(height=35)
                                with dpg.group(horizontal=True):
                                    dpg.add_spacer(width=20)
                                    self.render_dpad()
                                    dpg.add_spacer(width=60)

                            self.render_stick()

                    with dpg.group():
                        dpg.add_spacer(height=60)
                        with dpg.group(horizontal=True):
                            dpg.add_spacer(width=60)
                            self.render_right_buttons()

        tags = [
            "__btn_X",
            "__btn_Y",
            "__btn_A",
            "__btn_B",
            "__btn_dpad_u",
            "__btn_dpad_l",
            "__btn_dpad_r",
            "__btn_dpad_d",
            "__btn_sh_l",
            "__btn_sh_r",
            "__btn_tr_l",
            "__btn_tr_r",
            "__btn_back",
            "__btn_start",
        ]

        for tag in tags:
            dpg.bind_item_handler_registry(tag, "__btn_handler")


def main(argv):
    win_width = 580
    win_height = 250
    local = Path(__file__).parent
    init_path = local / "gui.ini"
    window = MainWindow(win_width, win_height)

    dpg.create_context()
    # dpg.configure_app(init_file=init_path, docking=True)
    dpg.configure_app()
    dpg.create_viewport(title="v360 GUI", width=win_width, height=win_height)
    dpg.setup_dearpygui()

    window.render()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main(sys.argv[1:])
