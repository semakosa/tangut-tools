# glosser_tab.py - Main content area for the Tangut Glossing Tool
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib
import os

from word_relation_widget import WordRelationshipWidget
from utils import GlossingModel

def set_clipboard(text, mime_type='text/plain'):
    """
    Set clipboard content with specified MIME type.
    
    Args:
        text: The text to copy to clipboard
        mime_type: The MIME type of the content (currently not used)
    """
    display = Gdk.Display.get_default()
    clipboard = display.get_clipboard()
    
    # In GTK4, we need to use this approach for text content
    clipboard.set(text)

class ContentArea(Gtk.Box):
    """
    Main content area for the Tangut glossing functionality.
    
    This class manages the main user interface components of the application,
    including text input, glossing editor, and text output areas.
    """
    
    def __init__(self):
        """Initialize the content area with all necessary UI components."""
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL, 
            spacing=10, 
            margin_top=10, 
            margin_bottom=10, 
            margin_start=10, 
            margin_end=10
        )
        
        # Create the configuration toolbar
        self.create_configuration_toolbar()
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        
        # Create the text input and Convert button
        self.create_input_and_button()
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Create the glossing editor
        self.create_glossing_editor()
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        
        # Create a rich text output area
        self.create_text_output()

    def create_configuration_toolbar(self):
        """Create the toolbar with configuration options."""
        config_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Add pronunciation system selector
        system_label = Gtk.Label(label="Pronunciation System:")
        config_toolbar.append(system_label)
        
        self.pronunciation_system = Gtk.ComboBoxText()
        self.pronunciation_system.append("GX202404", "Gong Xun 2024.04")
        self.pronunciation_system.append("GX202411", "Gong Xun 2024.11")
        self.pronunciation_system.set_active_id("GX202411")  # Default
        self.pronunciation_system.connect("changed", self.on_pronunciation_system_changed)
        config_toolbar.append(self.pronunciation_system)
        
        # Add spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        config_toolbar.append(spacer)
        
        # Add "About" button
        about_button = Gtk.Button(label="About")
        about_button.connect("clicked", self.on_about_clicked)
        config_toolbar.append(about_button)
        
        self.append(config_toolbar)

    def create_input_and_button(self):
        """Create the text input field and associated control buttons."""
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.text_input = Gtk.Entry()
        self.text_input.set_hexpand(True)
        self.text_input.set_placeholder_text("Enter Tangut text here...")
        self.text_input.connect("activate", self.on_convert_clicked)
        input_box.append(self.text_input)

        # Button to convert text
        convert_button = Gtk.Button(label="Convert")
        convert_button.connect("clicked", self.on_convert_clicked)
        input_box.append(convert_button)
        
        # Add paste button
        paste_button = Gtk.Button()
        paste_button.set_icon_name("edit-paste-symbolic")
        paste_button.set_tooltip_text("Paste from clipboard")
        paste_button.connect("clicked", self.on_paste_clicked)
        input_box.append(paste_button)
        
        # Add clear button
        clear_button = Gtk.Button()
        clear_button.set_icon_name("edit-clear-symbolic")
        clear_button.set_tooltip_text("Clear input field")
        clear_button.connect("clicked", self.on_clear_clicked)
        input_box.append(clear_button)
        
        self.append(input_box)

    def create_glossing_editor(self):
        """Create the word relationship widget for glossing editing."""
        model = GlossingModel([], [], [])
        
        self.word_relation_widget = WordRelationshipWidget(model)
        self.word_relation_widget.connect("content-changed", self.on_content_changed)
        self.word_relation_widget.connect("export-clicked", self.on_export_clicked)
        self.append(self.word_relation_widget)

    def create_text_output(self):
        """Create the text output area with copy functionality."""
        output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Add a label with buttons for the output section
        output_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        output_label = Gtk.Label(label="Output:")
        output_label.set_xalign(0)  # Left-align the label
        output_header.append(output_label)
        
        # Add spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        output_header.append(spacer)
        
        # Add copy button for the output
        copy_button = Gtk.Button()
        copy_button.set_icon_name("edit-copy-symbolic")
        copy_button.set_tooltip_text("Copy output to clipboard")
        copy_button.connect("clicked", self.on_copy_output_clicked)
        output_header.append(copy_button)
        
        output_box.append(output_header)
        
        # Create scrolled window for the output
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        
        self.text_output = Gtk.TextView()
        self.text_output.set_editable(False)
        self.text_output.set_cursor_visible(False)
        self.text_output.set_wrap_mode(Gtk.WrapMode.NONE)
        scrolled_window.set_child(self.text_output)
        
        output_box.append(scrolled_window)
        self.append(output_box)

    def on_about_clicked(self, button):
        """Display the about dialog with application information."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self.get_root())
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tangut Glossing Tool")
        about_dialog.set_version("1.0.0")
        about_dialog.set_comments("A standalone application for dynamic transcription and glossing of Tangut text.")
        about_dialog.set_website("https://github.com/user/tangut-tool")
        about_dialog.set_website_label("Project Repository")
        about_dialog.set_authors(["Contributors"])
        about_dialog.set_copyright("© 2023-2024")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        
        about_dialog.show()

    def on_pronunciation_system_changed(self, combobox):
        """
        Handle selection of a new pronunciation system.
        
        Args:
            combobox: The pronunciation system combobox widget
        """
        # Update the pronunciation system and refresh the display
        system = combobox.get_active_id()
        if hasattr(self, 'word_relation_widget') and self.word_relation_widget.model.words:
            # Refresh the data with the new pronunciation system
            try:
                self.word_relation_widget.update_pronunciation_system(system)
                self.word_relation_widget.update_status(f"Using {system} pronunciation system")
            except Exception as e:
                print(f"Error updating pronunciation system: {e}")
        
    def on_paste_clicked(self, button):
        """
        Paste text from clipboard and process it.
        
        Args:
            button: The paste button widget
        """
        display = Gdk.Display.get_default()
        clipboard = display.get_clipboard()
        
        text = clipboard.get_text()
        if text:
            self.text_input.set_text(text)
            self.on_convert_clicked(None)
        else:
            self.word_relation_widget.update_status("No text found in clipboard")
    
    def on_clear_clicked(self, button):
        """
        Clear the input field.
        
        Args:
            button: The clear button widget
        """
        self.text_input.set_text("")
        self.text_input.grab_focus()

    def on_copy_output_clicked(self, button):
        """
        Copy the output text to clipboard.
        
        Args:
            button: The copy button widget
        """
        buffer = self.text_output.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        if text:
            set_clipboard(text)
            self.word_relation_widget.update_status("Output copied to clipboard")

    def on_convert_clicked(self, widget):
        """
        Convert the input text to Tangut characters and process them.
        
        Args:
            widget: The widget that triggered the event
        """
        text = self.text_input.get_text()
        # Extract Tangut characters from the input text
        tangut_chars = [char for char in text if 0x17000 <= ord(char) <= 0x187FF]

        if not tangut_chars:
            self.text_output.get_buffer().set_text("No Tangut characters found in input text")
            self.word_relation_widget.update_status("No Tangut characters found")
            return

        # Create the GlossingModel with the detected characters
        dummy_model = GlossingModel(
            words=tangut_chars, 
            relationships=[" "] * (len(tangut_chars) - 1 if len(tangut_chars) > 0 else 0),
            glosses=[""] * len(tangut_chars)
        )

        # Get the current pronunciation system
        system = self.pronunciation_system.get_active_id()
        
        # Update the model of word_relation_widget
        self.word_relation_widget.set_model(dummy_model, system)

        # Update the text in the output area
        self.text_output.get_buffer().set_text('\t'.join(tangut_chars))
        self.word_relation_widget.update_status(f"Converted {len(tangut_chars)} Tangut characters")
        
    def on_content_changed(self, glossing):
        """
        Update the output text when content changes in the glossing editor.
        
        Args:
            glossing: The WordRelationshipWidget that triggered the event
        """
        data = glossing.data
        word_groups, relations = glossing.model.get_transformed_data()
        glosses = glossing.model.glosses

        # Format the output with the three rows (characters, pronunciation, glosses)
        row1 = ""  # Characters
        row2 = ""  # Pronunciation
        row3 = ""  # Glosses
        
        for i, (wg, gl) in enumerate(zip(word_groups, glosses)):
            # Add characters
            row1 += ''.join(wg)
            
            # Add pronunciations
            reconstructions = []
            for ch in wg:
                if ch in data:
                    reconstructions.append(data[ch].reconstruction)
                else:
                    reconstructions.append("?")
            row2 += '.'.join(reconstructions)
            
            # Add glosses
            if i < len(gl) and not gl:
                gl = '?'
            row3 += gl

            # Add relationships between word groups
            if i < len(relations):
                rel = relations[i]
                if rel == ' ':
                    rel = '\t'
                row1 += rel
                row2 += rel
                row3 += rel

        self.text_output.get_buffer().set_text('\n'.join([row1, row2, row3]))
        
    def on_export_clicked(self, glossing):
        """
        Export the current output to clipboard.
        
        Args:
            glossing: The WordRelationshipWidget that triggered the event
        """
        # Get the content from the output area
        buffer = self.text_output.get_buffer()
        start, end = buffer.get_bounds()
        text_content = buffer.get_text(start, end, False)
        
        # Simply copy to clipboard
        if text_content:
            set_clipboard(text_content)
            self.word_relation_widget.update_status("Output copied to clipboard")
        else:
            self.word_relation_widget.update_status("No content to export")
