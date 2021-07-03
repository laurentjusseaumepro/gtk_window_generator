import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

WIDTH_WINDOW          = 1000
HEIGHT_WINDOW         = 720

class MyWindow(Gtk.Window):
    def start(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

    def set_controller(self, controller):
        self.controller = controller

    def __init__(self):
        Gtk.Window.__init__(self, title="Home Config")
        self.set_default_size(WIDTH_WINDOW, HEIGHT_WINDOW)
        