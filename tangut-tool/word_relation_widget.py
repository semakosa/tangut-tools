import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject, Gdk, Pango

from utils import GlossingModel, fetch_data

class WordRelationshipWidget(Gtk.Grid):
    """
    A widget for managing Tangut word relationships in a grid layout.
    
    This widget displays Tangut characters with their pronunciation and glosses, 
    and allows users to define relationships between characters to form word groups.
    It also handles the display of glosses and exports the content.
    """
    
    # Define custom signals for widget communication
    __gsignals__ = {
        'content-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'export-clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'help-clicked': (GObject.SignalFlags.RUN_FIRST, None, ())
    }
    
    def __init__(self, model):
        """
        Initialize the word relationship widget.
        
        Args:
            model: A GlossingModel instance that contains the data to display
        """
        super().__init__()
        self.set_row_spacing(8)
        self.set_column_spacing(8)
        self.widgets = []  # List to keep track of created widgets
        self.model = model
        self.data = {}  # Dictionary to store character data
        self.pronunciation_system = 'GX202411'  # Default pronunciation system
        
        # Create a status bar
        self.create_status_bar()

    def create_status_bar(self):
        """Create a status bar at the bottom of the widget."""
        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        status_bar.set_margin_start(8)
        status_bar.set_margin_end(8)
        status_bar.set_margin_top(8)
        status_bar.set_margin_bottom(8)
        
        # Item count label
        self.status_label = Gtk.Label(label="No items loaded")
        status_bar.append(self.status_label)
        status_bar.set_hexpand(True)
        
        # Attach to the grid - this will be updated in repopulate_grid to be at the bottom
        self.status_bar = status_bar
        self.widgets.append(status_bar)

    def on_export_clicked(self, button):
        """Handle the export button click event."""
        self.emit('export-clicked')
    
    def on_key_pressed(self, controller, keyval, keycode, state):
        """
        Handle keyboard shortcuts.
        
        Args:
            controller: The event controller
            keyval: The key value
            keycode: The key code
            state: The modifier state
            
        Returns:
            True if the event was handled, False otherwise
        """
        modifiers = state & Gtk.accelerator_get_default_mod_mask()
        control_mask = Gdk.ModifierType.CONTROL_MASK
        
        # Check for Ctrl+E (Export)
        if keyval == Gdk.KEY_e and modifiers == control_mask:
            self.on_export_clicked(None)
            return True
            
        # Check for F1 (Help)
        if keyval == Gdk.KEY_F1:
            self.emit('help-clicked')
            return True
            
        return False  # Event not handled

    def update_status(self, message):
        """Update the status bar message."""
        self.status_label.set_text(message)
        
    def update_pronunciation_system(self, system):
        """
        Update the pronunciation system and refresh the display.
        
        Args:
            system: The new pronunciation system identifier
        """
        if system != self.pronunciation_system:
            self.pronunciation_system = system
            # Re-fetch data for all characters with the new system
            for ch in self.data:
                self.data[ch] = fetch_data(ch, reconstruction_choice=system)
            # Redraw the UI
            self.repopulate_grid()
            self.emit('content-changed')

    def repopulate_grid(self):
        """Refresh the grid display with the current model data."""
        # Clear the existing widgets
        for widget in self.widgets:
            # Only try to remove widget if it's still attached to this grid
            if widget.get_parent() == self:
                self.remove(widget)
        self.widgets.clear()
        
        # Get the model's current state
        words, relationships, glosses = self.model.get_current_state()
        transformed_words, transformed_relationships = self.model.get_transformed_data()

        # Create an outer FlowBox to handle the wrapping layout
        outer_flow = Gtk.FlowBox()
        outer_flow.set_valign(Gtk.Align.START)
        outer_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        outer_flow.set_max_children_per_line(15)  # Allow more items per row
        outer_flow.set_min_children_per_line(1)
        outer_flow.set_row_spacing(10)
        outer_flow.set_column_spacing(8)  # Slightly more spacing between columns
        outer_flow.set_homogeneous(False)
        
        # Track relationship indices in the original model
        relationship_index = 0
        
        # Process each word group
        for i, word_group in enumerate(transformed_words):
            # Create a box to hold the character group and its separator
            group_with_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            group_with_separator.set_margin_start(2)
            group_with_separator.set_margin_end(2)
            
            # Create the frame for the character group
            frame = Gtk.Frame()
            frame.add_css_class("frame")
            frame_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            frame_child.set_margin_start(4)
            frame_child.set_margin_end(4)
            frame_child.set_margin_top(4)
            frame_child.set_margin_bottom(4)
            frame.set_child(frame_child)
            
            # Container for character display and internal relationship selectors
            character_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            character_container.set_halign(Gtk.Align.CENTER)
            
            # Process each character in the word group
            for j, ch in enumerate(word_group):
                # If not the first character in a group, add an internal relationship selector
                if j > 0:
                    # Create a relationship selector for internal characters
                    internal_selector = self.create_relationship_selector(".", relationship_index - 1, True)
                    internal_selector.set_tooltip_text("Change to split this word group")
                    character_container.append(internal_selector)
                
                # Add the character display
                char_label = Gtk.Label()
                char_label.set_markup(f"<span font='20'>{ch}</span>")
                character_container.append(char_label)
                
                # Increment relationship index if not the last character
                if j < len(word_group) - 1:
                    relationship_index += 1
            
            # Add the character container to the column
            frame_child.append(character_container)
            
            # Format the transcription
            transcription = []
            for ch in word_group:
                if ch in self.data:
                    transcription.append(self.data[ch].reconstruction)
                else:
                    transcription.append("?")
            
            transcription_text = '.'.join(transcription)
            transcription_field = Gtk.Label(label=transcription_text)
            transcription_field.set_halign(Gtk.Align.CENTER)
            frame_child.append(transcription_field)
            
            # Format the gloss field with candidates
            gloss_candidates = set()
            for ch in word_group:
                if ch in self.data:
                    gloss_candidates.update(self.data[ch].semantics)
            
            gloss_candidates = sorted(gloss_candidates)
            if i < len(glosses) and glosses[i] and glosses[i] not in gloss_candidates:
                gloss_candidates = [glosses[i]] + gloss_candidates
            
            # Create the combo box with a narrower initial width
            gloss_combo_box = Gtk.ComboBoxText.new_with_entry()
            
            # Configure the gloss entry for better sizing
            gloss_entry = gloss_combo_box.get_child()
            gloss_entry.set_max_width_chars(3)  # Limit maximum expansion
            
            # Make the combo box and its containers not expand
            gloss_combo_box.set_hexpand(False)
            frame.set_hexpand(False)
            frame_child.set_hexpand(False)
            character_container.set_hexpand(False)
            
            # Add CSS to control the width more directly
            context = gloss_entry.get_style_context()
            provider = Gtk.CssProvider()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

            # Fill with candidates
            for candidate in gloss_candidates:
                gloss_combo_box.append_text(candidate)
                
            if i < len(glosses):
                gloss_combo_box.get_child().set_text(glosses[i])
            gloss_combo_box.connect("changed", self.on_gloss_changed, i)
            frame_child.append(gloss_combo_box)
            
            # Add the frame to the group box
            group_with_separator.append(frame)
            
            # Add relationship selector outside the frame if needed
            if i < len(transformed_relationships):
                relationship_selector = self.create_relationship_selector(
                    transformed_relationships[i], 
                    relationship_index
                )
                relationship_selector.set_valign(Gtk.Align.CENTER)
                relationship_index += 1
                group_with_separator.append(relationship_selector)
            
            # Create a FlowBox.FlowBoxChild for this character group
            flow_child = Gtk.FlowBoxChild()
            flow_child.set_child(group_with_separator)
            
            # Add to outer flow box
            outer_flow.append(flow_child)
        
        # Create a container to hold the header and the flowbox
        main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Add a scrolled window to contain the flowbox
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_margin_start(8)
        scrolled_window.set_margin_end(8)
        scrolled_window.set_margin_top(8)
        scrolled_window.set_margin_bottom(8)
        scrolled_window.set_child(outer_flow)
        main_container.append(scrolled_window)
        
        # Add the main container to the grid
        self.attach(main_container, 0, 1, 2, 1)
        self.widgets.append(main_container)
        
        # Add the status bar at the bottom
        self.create_status_bar()
        self.attach(self.status_bar, 0, 2, 2, 1)
        self.widgets.append(self.status_bar)
        
        # Update status with item count
        item_count = len(transformed_words)
        if item_count > 0:
            self.update_status(f"{item_count} items loaded")
        else:
            self.update_status("No items loaded")

    def create_relationship_selector(self, active_id, pos, is_internal=False):
        """
        Create a dropdown for selecting the relationship between characters or words.
        
        Args:
            active_id: The initially active relationship type
            pos: The position index in the model
            is_internal: Whether this is an internal relationship within a word group
            
        Returns:
            A configured Gtk.ComboBoxText widget
        """
        relationship_selector = Gtk.ComboBoxText()
        
        # Add relationship options (space, hyphen, dot)
        # Note: These options are intentionally kept separate for both internal and external selectors
        # to allow for full flexibility in splitting and joining words
        relationship_selector.append(" ", " ")
        relationship_selector.append("-", "-")
        relationship_selector.append(".", ".")
        
        # Configure the selector's appearance based on type
        if is_internal:
            # Make internal selectors more compact
            relationship_selector.set_size_request(35, -1)
            relationship_selector.set_tooltip_text("Change to split this word group")
        else:
            # External selectors should be slightly larger
            relationship_selector.set_size_request(40, -1)
            relationship_selector.set_valign(Gtk.Align.CENTER)
            relationship_selector.set_tooltip_text("Relationship to next word")
        
        relationship_selector.set_active_id(active_id)
        relationship_selector.connect("changed", self.on_relationship_changed, pos)
        
        return relationship_selector

    def on_relationship_changed(self, widget, widget_id):
        """
        Handle when a relationship between words is changed.
        
        Args:
            widget: The relationship selector widget
            widget_id: The position index in the model
        """
        new_relation = widget.get_active_id()
        print(f"Relationship {widget_id} changed to: {new_relation}")
        
        self.model.update_relationship(widget_id, new_relation)
        self.repopulate_grid()
        self.emit('content-changed')  # Emit the custom signal

    def on_gloss_changed(self, widget, widget_id):
        """
        Handle when a gloss is changed.
        
        Args:
            widget: The gloss combobox widget
            widget_id: The position index in the model
        """
        new_gloss = widget.get_active_text()
        print(f"Gloss {widget_id} changed to: {new_gloss}")
        
        self.model.update_gloss(widget_id, new_gloss)
        self.emit('content-changed')  # Emit the custom signal

    def set_model(self, new_model, pronunciation_system=None):
        """
        Set a new model and update the pronunciation system if provided.
        
        Args:
            new_model: The new GlossingModel to display
            pronunciation_system: Optional new pronunciation system to use
        """
        self.model = new_model
        
        # Update pronunciation system if specified
        if pronunciation_system:
            self.pronunciation_system = pronunciation_system
            
        # Fetch data for all characters in the model
        for ch in set(sum([[ch] if isinstance(ch, str) else ch for ch in self.model.words], [])):
            self.data[ch] = fetch_data(ch, reconstruction_choice=self.pronunciation_system)
            # print(f"Fetched data for {ch}: {self.data[ch]}")
            
        # Redraw the UI
        self.repopulate_grid()
