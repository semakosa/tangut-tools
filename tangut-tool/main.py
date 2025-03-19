#!/usr/bin/env python3
# Tangut Glossing Tool - Main application
"""
Tangut Glossing Tool

A standalone application for dynamic transcription and glossing of Tangut text.
This module contains the main application class and entry point.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Gio
import sys
import os

import glosser_tab

class TangutGlossingApp(Adw.Application):
    """
    Main application class for the Tangut Glossing Tool.
    
    This class manages the application lifecycle, windows, and global actions.
    """
    
    def __init__(self):
        """Initialize the application with all necessary settings and connections."""
        # Initialize the application
        super().__init__(application_id="org.example.TangutGlossingTool")
        
        # Connect to the activate signal
        self.connect("activate", self.on_activate)
        
        # Set up keyboard shortcuts for the app
        self.setup_keyboard_shortcuts()
        
        # Create application actions
        self.create_actions()
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard accelerators for common actions."""
        self.set_accels_for_action("app.new-window", ["<Control>n"])
        self.set_accels_for_action("app.quit", ["<Control>q"])
        self.set_accels_for_action("app.help", ["F1"])
        
    def create_actions(self):
        """Create application-wide actions and connect them to handlers."""
        actions = [
            ("new-window", self.on_new_window),
            ("about", self.on_about),
            ("help", self.on_shortcuts_clicked),
            ("quit", self.on_quit)
        ]
        
        for action_name, callback in actions:
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", callback)
            self.add_action(action)
    
    def on_activate(self, app):
        """
        Handle application activation event.
        
        This is called when the application is launched.
        
        Args:
            app: The application instance
        """
        # Get existing windows
        windows = self.get_windows()
        
        if windows:
            # If we have a window already, present it
            windows[0].present()
        else:
            # Create a new window
            win = self.create_window()
            win.present()
    
    def create_window(self):
        """
        Create and configure a new application window.
        
        Returns:
            A configured Adw.ApplicationWindow instance
        """
        # Create an application window
        window = Adw.ApplicationWindow(application=self)
        window.set_title("Tangut Glossing Tool")
        window.set_default_size(1000, 750)
        window.set_icon_name("accessories-text-editor")
        
        # Create a header bar
        header = Adw.HeaderBar()
        
        # Add menu button to the header bar
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        
        # Create a menu model
        menu_builder = Gtk.Builder.new_from_string("""
        <?xml version="1.0" encoding="UTF-8"?>
        <interface>
            <menu id="app-menu">
                <section>
                    <item>
                        <attribute name="label">New Window</attribute>
                        <attribute name="action">app.new-window</attribute>
                    </item>
                </section>
                <section>
                    <item>
                        <attribute name="label">Help</attribute>
                        <attribute name="action">app.help</attribute>
                    </item>
                    <item>
                        <attribute name="label">About</attribute>
                        <attribute name="action">app.about</attribute>
                    </item>
                    <item>
                        <attribute name="label">Quit</attribute>
                        <attribute name="action">app.quit</attribute>
                    </item>
                </section>
            </menu>
        </interface>
        """, -1)
        
        popover = Gtk.PopoverMenu.new_from_model(menu_builder.get_object("app-menu"))
        menu_button.set_popover(popover)
        header.pack_end(menu_button)
        
        # Create a vertical box to hold all widgets
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Add the header bar
        main_box.append(header)
        
        # Create a notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_vexpand(True)
        main_box.append(notebook)
        
        # Add the glosser tab
        glosser_content = glosser_tab.ContentArea()
        page = Gtk.Box()
        page.set_hexpand(True)
        page.set_vexpand(True)
        page.append(glosser_content)
        
        glosser_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        icon = Gtk.Image.new_from_icon_name("accessories-text-editor")
        glosser_label.append(icon)
        glosser_label.append(Gtk.Label(label="Glosser"))
        
        notebook.append_page(page, glosser_label)
        
        # Create a status bar
        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        status_bar.set_margin_start(8)
        status_bar.set_margin_end(8)
        status_bar.set_margin_top(4)
        status_bar.set_margin_bottom(4)
        
        status_label = Gtk.Label(label="Ready")
        status_bar.append(status_label)
        status_bar.set_hexpand(True)
        
        # Add a version label to the status bar
        version_label = Gtk.Label(label="v0.0.1")
        version_label.set_xalign(1.0)  # Right-align
        status_bar.append(version_label)
        
        main_box.append(status_bar)
        
        # Set the window content
        window.set_content(main_box)
        
        return window
    
    def on_new_window(self, action, param):
        """
        Create and show a new application window.
        
        Args:
            action: The triggered action
            param: Action parameters
        """
        win = self.create_window()
        win.present()
    
    def on_about(self, action, param):
        """
        Show the about dialog.
        
        Args:
            action: The triggered action
            param: Action parameters
        """
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self.get_active_window())
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tangut Glossing Tool")
        about_dialog.set_version("0.0.1")
        about_dialog.set_comments("A standalone application for dynamic transcription and glossing of Tangut text.")
        about_dialog.set_website("https://github.com/semakosa/tangut-tools")
        about_dialog.set_website_label("Project Repository")
        about_dialog.set_authors(["Xun Gong (University of Vienna)", "and collaborators"])
        about_dialog.set_copyright("© 2025 Xun Gong and collaborators")
        about_dialog.set_license_type(Gtk.License.MIT_X11)
        
        about_dialog.present()
    
    def on_quit(self, action, param):
        """
        Quit the application.
        
        Args:
            action: The triggered action
            param: Action parameters
        """
        self.quit()
    
    def on_shortcuts_clicked(self, action, param):
        """
        Show keyboard shortcuts window.
        
        Args:
            action: The triggered action
            param: Action parameters
        """
        builder = Gtk.Builder.new_from_string("""
        <?xml version="1.0" encoding="UTF-8"?>
        <interface>
            <object class="GtkShortcutsWindow" id="shortcuts-window">
                <property name="modal">1</property>
                <child>
                    <object class="GtkShortcutsSection">
                        <property name="section-name">shortcuts</property>
                        <property name="max-height">12</property>
                        <child>
                            <object class="GtkShortcutsGroup">
                                <property name="title">General</property>
                                <child>
                                    <object class="GtkShortcutsShortcut">
                                        <property name="accelerator">&lt;ctrl&gt;n</property>
                                        <property name="title">New Window</property>
                                    </object>
                                </child>
                                <child>
                                    <object class="GtkShortcutsShortcut">
                                        <property name="accelerator">&lt;ctrl&gt;q</property>
                                        <property name="title">Quit</property>
                                    </object>
                                </child>
                            </object>
                        </child>
                        <child>
                            <object class="GtkShortcutsGroup">
                                <property name="title">Glossing</property>
                                <child>
                                    <object class="GtkShortcutsShortcut">
                                        <property name="accelerator">&lt;ctrl&gt;e</property>
                                        <property name="title">Export</property>
                                    </object>
                                </child>
                                <child>
                                    <object class="GtkShortcutsShortcut">
                                        <property name="accelerator">F1</property>
                                        <property name="title">Help</property>
                                    </object>
                                </child>
                            </object>
                        </child>
                    </object>
                </child>
            </object>
        </interface>
        """, -1)
        
        window = builder.get_object("shortcuts-window")
        window.set_transient_for(self.get_active_window())
        window.present()

def main():
    """
    Main entry point for the application.
    
    Returns:
        The application exit code
    """
    # Initialize Adw
    Adw.init()
    
    # Create and run the application
    app = TangutGlossingApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())

