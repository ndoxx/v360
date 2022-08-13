#!/usr/bin/python3
import sys
import dearpygui.dearpygui as gui
from pathlib import Path
import numpy as np
from v360 import FFXController


EPS = 1e-5


class StickWindow:
    def __init__(self, size):
        self.size = size
        self.center = [size/2, size/2]
        self.thickness = 5
        self.outer_radius = 0.75*(size/2 - self.thickness / 2)
        self.inner_radius = size/20
        self.color = [128, 128, 128]
        self.position = self.center

    def update_stick(self, controller):
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
        controller.set_movement(*ctl_pos)

        gui.apply_transform(
            "__stick_node", gui.create_translation_matrix(list(pos)))

    def render(self, controller):
        def on_mouse_down(sender, data):
            if gui.is_item_hovered('__canvas'):
                self.position = gui.get_drawing_mouse_pos()
                self.update_stick(controller)

        def on_mouse_release(sender, data):
            self.position = self.center
            self.update_stick(controller)

        with gui.handler_registry():
            gui.add_mouse_drag_handler(callback=on_mouse_down)
            gui.add_mouse_click_handler(callback=on_mouse_down)
            gui.add_mouse_release_handler(callback=on_mouse_release)

        with gui.window(label="Analog Stick", tag="__stick_window"):
            with gui.drawlist(width=self.size, height=self.size, tag="__canvas"):
                # Background circle
                gui.draw_circle(center=self.center,
                                radius=self.outer_radius, color=self.color, thickness=self.thickness)
                # Movable stick
                with gui.draw_node(tag="__stick_node"):
                    gui.draw_circle(center=self.position,
                                    radius=self.inner_radius, fill=self.color)


def main(argv):
    local = Path(__file__).parent
    init_path = local / "gui.ini"
    ctl = FFXController()
    stick = StickWindow(150)

    gui.create_context()
    gui.configure_app(init_file=init_path, docking=True)
    gui.create_viewport(title="v360 GUI", width=600, height=300)
    gui.setup_dearpygui()

    stick.render(ctl)

    gui.show_viewport()
    gui.start_dearpygui()
    gui.destroy_context()


if __name__ == '__main__':
    main(sys.argv[1:])
