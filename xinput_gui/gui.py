# gui.py - graphical user interface
# Copyright (C) 2019  Ivan Fonseca
#
# This file is part of xinput-gui.
#
# xinput-gui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the # License,
# or (at your option) any later version.
#
# xinput-gui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xinput-gui.  If not, see <https://www.gnu.org/licenses/>.

'''Graphical user interface.'''

from .xinput import get_devices, get_device_props, set_device_prop
from pkg_resources import resource_filename
from typing import Dict, Union

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


__version__ = '0.1.1'


class Gui:
    def __init__(self):
        # Create interface
        self.builder = Gtk.Builder()
        # Find interface file
        self.builder.add_from_file(
            resource_filename('xinput_gui', 'app.glade'))

        self.builder.connect_signals(Gui.SignalHandler(self))

        # Main window widgets
        self.win_app = self.builder.get_object("win_app")
        self.btn_edit = self.builder.get_object("btn_edit")
        self.store_devices = self.builder.get_object("store_devices")
        self.store_props = self.builder.get_object("store_props")
        self.tree_devices_selection = self.builder.get_object(
            "tree_devices_selection")
        self.tree_props_selection = self.builder.get_object(
            "tree_props_selection")
        self.tree_column_props_id = self.builder.get_object(
            "tree_column_props_id")

        # Edit window widgets
        self.win_edit = self.builder.get_object("win_edit")
        self.entry_old_val = self.builder.get_object("entry_old_val")
        self.entry_new_val = self.builder.get_object("entry_new_val")
        self.btn_edit_cancel = self.builder.get_object("btn_edit_cancel")
        self.btn_edit_apply = self.builder.get_object("btn_edit_apply")

        # Settings window widgets
        self.win_settings = self.builder.get_object("win_settings")
        self.btn_settings_save = self.builder.get_object("btn_settings_save")
        self.chk_hide_prop_ids = self.builder.get_object("chk_hide_prop_ids")

        self.refresh_devices()
        self.win_app.set_title("Xinput GUI {}".format(__version__))
        self.win_app.show_all()

        # About window widgets
        self.win_about = self.builder.get_object("win_about")
        self.win_about.set_version(__version__)

        Gtk.main()

    def refresh_devices(self):
        self.store_devices.clear()
        self.store_props.clear()
        self.tree_devices_selection.unselect_all()
        self.tree_props_selection.unselect_all()
        self.btn_edit.set_sensitive(False)

        for device in get_devices():
            self.store_devices.append([
                int(device['id']),
                device['name'],
                device['type']
            ])

    def show_device(self, device_id: int):
        self.store_props.clear()
        self.tree_props_selection.unselect_all()
        self.btn_edit.set_sensitive(False)

        for prop in get_device_props(device_id):
            self.store_props.append([
                int(prop['id']),
                prop['name'],
                prop['val']
            ])

    def get_selected_device(self) -> Dict[str, Union[str, int]]:
        model, treeiter = self.tree_devices_selection.get_selected()
        return({
            'id': model[treeiter][0],
            'name': model[treeiter][1],
            'type': model[treeiter][2],
        })

    def get_selected_prop(self) -> Dict[str, Union[str, int]]:
        model, treeiter = self.tree_props_selection.get_selected()
        return({
            'id': model[treeiter][0],
            'name': model[treeiter][1],
            'val': model[treeiter][2],
        })

    def show_settings_window(self):
        # Get settings and update controls
        if self.tree_column_props_id.get_visible():
            self.chk_hide_prop_ids.set_active(False)
        else:
            self.chk_hide_prop_ids.set_active(True)

        self.btn_settings_save.set_sensitive(False)
        self.win_settings.show_all()

    def save_settings(self):
        # Get settings
        hide_prop_ids = self.chk_hide_prop_ids.get_active()

        # Save settings
        # TODO

        # Apply settings to active program
        if hide_prop_ids:
            self.tree_column_props_id.set_visible(False)
        else:
            self.tree_column_props_id.set_visible(True)

    class SignalHandler:
        def __init__(self, gui):
            self.gui = gui

        # Main window signals

        def on_win_app_destroy(self, *args):
            Gtk.main_quit()

        def on_menu_settings_activate(self, menu: Gtk.MenuItem):
            self.gui.show_settings_window()

        def on_menu_about_activate(self, menu: Gtk.MenuItem):
            self.gui.win_about.run()

        def on_btn_refresh_clicked(self, button: Gtk.Button):
            self.gui.refresh_devices()

        def on_device_selected(self, selection: Gtk.TreeSelection):
            self.gui.show_device(self.gui.get_selected_device()['id'])

        def on_prop_selected(self, selection: Gtk.TreeSelection):
            self.gui.btn_edit.set_sensitive(True)

        def on_btn_edit_clicked(self, button: Gtk.Button):
            prop = self.gui.get_selected_prop()

            self.gui.entry_old_val.set_text(prop['val'])
            self.gui.entry_new_val.set_text(prop['val'])
            self.gui.win_edit.show_all()
            self.gui.entry_new_val.grab_focus()

        # Edit window signals

        def on_entry_new_val_activate(self, entry: Gtk.Entry):
            self.gui.btn_edit_apply.clicked()

        def on_btn_edit_apply_clicked(self, button: Gtk.Button):
            device = self.gui.get_selected_device()
            prop = self.gui.get_selected_prop()

            new_prop_val = self.gui.entry_new_val.get_text()

            # Update prop
            set_device_prop(device['id'], prop['id'], new_prop_val)

            # Update store
            model, treeiter = self.gui.tree_props_selection.get_selected()
            model[treeiter][2] = new_prop_val

            # Close edit window
            self.gui.win_edit.hide()

        def on_btn_edit_cancel_clicked(self, button: Gtk.Button):
            self.gui.win_edit.hide()

        # Settings window signals

        def on_btn_settings_save_clicked(self, button: Gtk.Button):
            self.gui.save_settings()
            self.gui.win_settings.hide()

        def on_btn_settings_cancel_clicked(self, button: Gtk.Button):
            self.gui.win_settings.hide()

        def on_chk_hide_prop_ids_toggled(self, chk_btn: Gtk.CheckButton):
            self.gui.btn_settings_save.set_sensitive(True)

        # About window signals

        def on_win_about_response(self, a, b):
            # TODO: close this properly
            self.gui.win_about.hide()


def main():
    """Start xinput-gui."""
    Gui()
