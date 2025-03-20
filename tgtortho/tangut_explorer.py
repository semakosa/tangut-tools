#!/usr/bin/env python3
"""
Tangut Explorer - A GTK application for exploring Tangut reconstruction models.

This application allows users to select different Tangut reconstruction models
and experiment with phonological features to see the resulting syllables.
"""

import gi
import inspect
import importlib
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk

# Import all available models dynamically
import tgtortho.models


def get_all_models():
    """Dynamically discover all available models."""
    models = {}
    # Get all members from tgtortho.models
    for name, obj in inspect.getmembers(tgtortho.models):
        if name.startswith('GX') or name.startswith('Ghc') and isinstance(obj, dict):
            # Check if it has the expected structure with 'phonology' and 'orthographies' keys
            if isinstance(obj, dict) and 'phonology' in obj and 'orthographies' in obj:
                # Use reconstruction_id as the display name
                reconstruction_id = obj['phonology'].reconstruction_id
                models[reconstruction_id] = obj
        # For backward compatibility, also look for orthography classes
        elif (name.endswith('Orthography') or name.endswith('_Orthography')) and inspect.isclass(obj):
            # Get the corresponding Vector class name
            if name.endswith('_Orthography'):
                vector_name = name.replace('_Orthography', '_Vector')
            else:
                vector_name = name.replace('Orthography', 'Vector')
                
            vector_class = getattr(tgtortho.models, vector_name, None)
            
            if vector_class:
                # Use reconstruction_id as the display name
                reconstruction_id = vector_class.reconstruction_id
                # If we haven't already added this model through the new approach
                if reconstruction_id not in models:
                    models[reconstruction_id] = {
                        'phonology': vector_class,
                        'orthographies': {'standard': obj}
                    }
    
    return models


class TangutExplorer(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.tangut.explorer")
        self.connect("activate", self.on_activate)
        self.model_name = None
        self.vector_class = None
        self.ortho_class = None
        self.orthographies = None
        self.current_orthography = None
        self.current_vector = None
        self.feature_widgets = {}
        self.models = get_all_models()
        
    def on_activate(self, app):
        self.win = Gtk.ApplicationWindow(application=app)
        self.win.set_title("Tangut Explorer")
        self.win.set_default_size(900, 600)
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        self.win.set_child(main_box)
        
        # Model selector
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        model_label = Gtk.Label(label="Select Model:")
        model_box.append(model_label)
        
        model_dropdown = Gtk.DropDown.new_from_strings(list(self.models.keys()))
        model_dropdown.connect("notify::selected", self.on_model_changed)
        model_box.append(model_dropdown)
        
        # Orthography selector (will be populated when model is selected)
        ortho_label = Gtk.Label(label="Orthography:")
        ortho_label.set_margin_start(20)
        model_box.append(ortho_label)
        
        self.ortho_dropdown = Gtk.DropDown()
        self.ortho_dropdown.connect("notify::selected", self.on_orthography_changed)
        model_box.append(self.ortho_dropdown)
        
        main_box.append(model_box)
        
        # Features area
        self.features_frame = Gtk.Frame(label="Phonological Features")
        self.features_frame.set_margin_top(10)
        
        # Scrolled window for features
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_min_content_height(300)
        
        # Use a grid for horizontal layout of features
        self.features_grid = Gtk.Grid()
        self.features_grid.set_column_spacing(10)
        self.features_grid.set_row_spacing(10)
        self.features_grid.set_margin_start(10)
        self.features_grid.set_margin_end(10)
        self.features_grid.set_margin_top(10)
        self.features_grid.set_margin_bottom(10)
        
        scrolled_window.set_child(self.features_grid)
        self.features_frame.set_child(scrolled_window)
        main_box.append(self.features_frame)
        
        # Result display area
        result_frame = Gtk.Frame(label="Result")
        result_frame.set_margin_top(10)
        result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        result_box.set_margin_start(10)
        result_box.set_margin_end(10)
        result_box.set_margin_top(10)
        result_box.set_margin_bottom(10)
        
        self.result_label = Gtk.Label()
        self.result_label.set_markup("<big><b>Select a model to begin</b></big>")
        self.result_label.set_margin_top(20)
        self.result_label.set_margin_bottom(20)
        result_box.append(self.result_label)
        
        result_frame.set_child(result_box)
        main_box.append(result_frame)
        
        # Initial model selection (first in list)
        if len(self.models) > 0:
            model_dropdown.set_selected(0)
        
        self.win.present()
    
    def on_model_changed(self, dropdown, param):
        # Clear previous features
        while self.features_grid.get_first_child():
            self.features_grid.remove(self.features_grid.get_first_child())
        
        self.feature_widgets = {}
        
        # Get selected model
        model_idx = dropdown.get_selected()
        self.model_name = list(self.models.keys())[model_idx]
        model_data = self.models[self.model_name]
        
        # Update vector class and orthographies
        self.vector_class = model_data['phonology']
        self.orthographies = model_data['orthographies']
        
        # Update orthography dropdown
        ortho_names = list(self.orthographies.keys())
        string_list = Gtk.StringList()
        for name in ortho_names:
            string_list.append(name)
        self.ortho_dropdown.set_model(string_list)
        self.ortho_dropdown.set_selected(0)  # Select the first orthography
        
        # Set the current orthography class
        self.current_orthography = ortho_names[0]
        self.ortho_class = self.orthographies[self.current_orthography]
        
        # Determine grid layout - try to make features appear in rows of 3-4 items
        features = [f for f in self.vector_class.specification.keys() if f != 'reconstruction_id']
        num_features = len(features)
        columns_per_row = min(4, max(2, num_features // 3 + (1 if num_features % 3 else 0)))
        
        # Update UI with features from the selected model
        row, col = 0, 0
        for feature in sorted(features):
            valid_values = self.vector_class.specification[feature]
                
            # Create a box for each feature
            feature_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            feature_box.set_margin_start(5)
            feature_box.set_margin_end(5)
            
            # Label for the feature
            label = Gtk.Label(label=f"{feature}:")
            label.set_xalign(0)
            feature_box.append(label)
            
            # Dropdown for feature values
            value_dropdown = Gtk.DropDown.new_from_strings(valid_values)
            feature_box.append(value_dropdown)
            
            # Store widget reference for later updates
            self.feature_widgets[feature] = value_dropdown
            
            # Connect change event
            value_dropdown.connect("notify::selected", self.on_feature_changed)
            
            # Add to grid
            self.features_grid.attach(feature_box, col, row, 1, 1)
            
            # Update position
            col += 1
            if col >= columns_per_row:
                col = 0
                row += 1
        
        # Initialize with default values
        self.update_vector_from_ui()
    
    def on_orthography_changed(self, dropdown, param):
        # Get selected orthography
        ortho_idx = dropdown.get_selected()
        ortho_names = list(self.orthographies.keys())
        self.current_orthography = ortho_names[ortho_idx]
        self.ortho_class = self.orthographies[self.current_orthography]
        
        # Update the display with the new orthography
        self.update_vector_from_ui()
    
    def on_feature_changed(self, dropdown, param):
        self.update_vector_from_ui()
    
    def update_vector_from_ui(self):
        if not self.vector_class or not self.ortho_class:
            return
            
        # Collect values from UI
        values = {}
        for feature, dropdown in self.feature_widgets.items():
            selected_idx = dropdown.get_selected()
            valid_values = self.vector_class.specification[feature]
            values[feature] = valid_values[selected_idx]
        
        try:
            # Create named tuple for the vector
            named_tuple = self.vector_class.namedtuple_type(**values)
            
            # Create vector and orthography
            self.current_vector = self.vector_class(named_tuple)
            orthography = self.ortho_class(self.current_vector)
            
            # Update result display
            representation = str(orthography)
            vector_repr = ", ".join([f"{k}: {v}" for k, v in sorted(values.items())])
            self.result_label.set_markup(
                f"<big><b>{representation}</b></big>\n\n"
                f"<small>Orthography: {self.current_orthography}</small>\n"
                f"<small>{vector_repr}</small>"
            )
        except Exception as e:
            self.result_label.set_markup(f"<span color='red'>Error: {str(e)}</span>")


if __name__ == "__main__":
    app = TangutExplorer()
    app.run(None) 