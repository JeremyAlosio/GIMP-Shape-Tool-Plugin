#!/usr/bin/env python

from gimpfu import *
import math
from collections import namedtuple
import gtk

CUSTOM_LAYER_NAME = "New Custom Shape Layer"

# Sample function for creating a preview dialog in GIMP Python
def show_dialog(image, drawable):

    dialog = gtk.Dialog("Draw Shape", None, gtk.DIALOG_DESTROY_WITH_PARENT)

    # Shape Type ComboBox
    shape_label = gtk.Label("Shape Type")
    dialog.vbox.pack_start(shape_label, False, False, 0)
    shape_combo = gtk.combo_box_new_text()
    for shape in ShapeOptions.labels:
        shape_combo.append_text(shape)
    shape_combo.set_active(ShapeOptions.CIRCLE)
    dialog.vbox.pack_start(shape_combo, False, False, 0)

    # Fill Type ComboBox
    fill_label = gtk.Label("Fill Type")
    dialog.vbox.pack_start(fill_label, False, False, 0)
    fill_combo = gtk.combo_box_new_text()
    for fill in FillOptions.labels:
        fill_combo.append_text(fill)
    fill_combo.set_active(FillOptions.FOREGROUND)
    dialog.vbox.pack_start(fill_combo, False, False, 0)

    # Fill Color Button
    color_label = gtk.Label("Custom Fill Color")
    dialog.vbox.pack_start(color_label, False, False, 0)
    color_button = gtk.ColorButton()
    dialog.vbox.pack_start(color_button, False, False, 0)

    # Outline Checkbox
    outline_checkbox = gtk.CheckButton("Outline")
    outline_checkbox.set_active(False)
    dialog.vbox.pack_start(outline_checkbox, False, False, 0)

    # Outline Color Button
    outline_color_label = gtk.Label("Outline Color")
    dialog.vbox.pack_start(outline_color_label, False, False, 0)
    outline_color_button = gtk.ColorButton()
    dialog.vbox.pack_start(outline_color_button, False, False, 0)

    # Outline Size SpinButton
    #outline_size_label = gtk.Label("Outline Size")
    #dialog.vbox.pack_start(outline_size_label, False, False, 0)
    #outline_size_spin = gtk.SpinButton()
    #outline_size_spin.set_range(1, 1000)
    #outline_size_spin.set_increments(1, 10)
    #outline_size_spin.set_value(5)
    #dialog.vbox.pack_start(outline_size_spin, False, False, 0)

    # Feathering Option
    #feather_label = gtk.Label("Feathering (pixels)")
    #dialog.vbox.pack_start(feather_label, False, False, 0)
    #feather_spin = gtk.SpinButton()
    #feather_spin.set_range(0, 100)
    #feather_spin.set_increments(1, 5)
    #feather_spin.set_value(0)
    #dialog.vbox.pack_start(feather_spin, False, False, 0)

    # Rounded Outline Checkbox
    rounded_checkbox = gtk.CheckButton("Rounded Outline")
    rounded_checkbox.set_active(False)
    dialog.vbox.pack_start(rounded_checkbox, False, False, 0)

    # Preview Button
    preview_button = gtk.Button("Preview")
    dialog.vbox.pack_start(preview_button, False, False, 0)

    dialog.show_all()

    # Define a preview function to draw the shape without committing
    def preview_shape(*args): 
        shape_type = shape_combo.get_active()
        fill_type = fill_combo.get_active()
        fill_color = color_button.get_color()
        outline = outline_checkbox.get_active()
        outline_color = outline_color_button.get_color()
        outline_size = outline_size_spin.get_value_as_int()
        feather_amount = feather_spin.get_value_as_int()
        rounded = rounded_checkbox.get_active()

        x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)[1:5]
        
        width, height = get_rectangle_dimensions(x1, y1, x2, y2)
        
        # Temporarily draw shape on image with preview mode
        draw_shape(
            image,
            shape_type,
            fill_type,
            (fill_color.red / 65535.0, fill_color.green / 65535.0, fill_color.blue / 65535.0),
            outline,
            (outline_color.red / 65535.0, outline_color.green / 65535.0, outline_color.blue / 65535.0),
            outline_size,
            feather_amount,
            rounded,
            x1,
            y1,
            width,
            height
        )

    # Connect preview to button and change events
    preview_button.connect("clicked", preview_shape)
    shape_combo.connect("changed", preview_shape)
    fill_combo.connect("changed", preview_shape)
    color_button.connect("color-set", preview_shape)
    outline_checkbox.connect("toggled", preview_shape)
    outline_size_spin.connect("value-changed", preview_shape)
    outline_color_button.connect("color-set", preview_shape)
    feather_spin.connect("value-changed", preview_shape)
    rounded_checkbox.connect("toggled", preview_shape)
    
    # Add Apply and Cancel buttons
    dialog.add_button("Apply", gtk.RESPONSE_OK)
    dialog.add_button("Cancel", gtk.RESPONSE_CANCEL)
    
    preview_shape()
    
    # Run the dialog and get the user input
    response = dialog.run()
    
    if response == gtk.RESPONSE_OK:
        merge_shape_layer(image)
    
    dialog.destroy()

def get_rectangle_dimensions(x1, y1, x2, y2):
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return width, height

def merge_shape_layer(image):
    merge_layer = pdb.gimp_image_get_layer_by_name(image, layer_name)
    pdb.gimp_image_merge_down(image, merge_layer, LAYER_MODE_NORMAL)

CUSTOM_LAYER_NAME = "New Custom Shape Layer"
def create_custom_layer(image, drawable):
    layer_name = CUSTOM_LAYER_NAME
    pdb.gimp_image_undo_group_start(image)
    # Check if the layer already exists
    existing_layer = pdb.gimp_image_get_layer_by_name(image, layer_name)
    
    if existing_layer is not None:
        if existing_layer.name == layer_name:
            existing_layer.name = "OLD_CUSTOM_SHAPE_LAYER_DELETE"
    
    # Create a new layer
    layer = pdb.gimp_layer_new(
        image, 
        drawable.width,
        drawable.height,
        RGBA_IMAGE,
        layer_name,
        100.0,
        LAYER_MODE_NORMAL
    )

    # Add the layer to the image
    pdb.gimp_image_insert_layer(image, layer, None, 0)  # Add to the top of the stack

    pdb.gimp_image_remove_layer(image, existing_layer)
    
    pdb.gimp_displays_flush()
    
    pdb.gimp_image_undo_group_end(image)
    
    return layer  # Return the newly created layer

# Function to create structured options for PF_OPTION
def createOptions(name, pairs):
    # Creates namedtuple with an index for each option, labels, and label-value pairs
    optsclass = namedtuple(name + 'Type', [symbol for symbol, label in pairs] + ['labels', 'labelTuples'])
    opts = optsclass(*(
        range(len(pairs)) +
        [[label for symbol, label in pairs]] +
        [[(label, i) for i, (symbol, label) in enumerate(pairs)]]
    ))
    return opts

# Define shape and fill options using the new createOptions function
ShapeOptions = createOptions('Shape', [('RECTANGLE', 'Rectangle'), ('ROUND_RECTANGLE', 'Round Rectangle'), ('CIRCLE', 'Circle'), ('TRIANGLE', 'Triangle'), ('STAR', 'Star')])
FillOptions = createOptions('Fill', [('FOREGROUND', 'Foreground'), ('BACKGROUND', 'Background'), ('CUSTOM', 'Custom')])

def draw_shape(image, shape_type, fill_type, fill_color, outline, outline_color, outline_size, feather_amount, rounded, x, y, width, height):
    # Create the custom layer and pass image and drawable
    newLayer = create_custom_layer(image, image.active_layer)

    pdb.gimp_context_push()
    pdb.gimp_image_undo_group_start(image)

    # Start by clearing any existing selection
    pdb.gimp_selection_none(image)

    # Draw shape based on shape_type
    if shape_type == ShapeOptions.RECTANGLE:
        pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, x, y, width, height)
    elif shape_type == ShapeOptions.ROUND_RECTANGLE:
        pdb.gimp_image_select_round_rectangle(image, CHANNEL_OP_REPLACE, x, y, width, height)
    elif shape_type == ShapeOptions.CIRCLE:
        diameter = min(width, height)
        pdb.gimp_image_select_ellipse(image, CHANNEL_OP_REPLACE, x, y, diameter, diameter)
    elif shape_type == ShapeOptions.TRIANGLE:
        # Triangle points (top, bottom-left, bottom-right)
        points = [(x + width / 2, y), (x, y + height), (x + width, y + height)]
        flat_points = [coord for point in points for coord in point]
        pdb.gimp_image_select_polygon(image, CHANNEL_OP_REPLACE, len(flat_points), flat_points)
    elif shape_type == ShapeOptions.STAR:
        # Center and radius setup
        center_x, center_y = x + width / 2, y + height / 2
        outer_radius = min(width, height) / 2
        inner_radius = outer_radius / 2
        points = []
        # Calculate star points
        for i in range(10):
            angle = i * math.pi / 5  # Half a point (alternates inner/outer points)
            radius = outer_radius if i % 2 == 0 else inner_radius
            points.append((center_x + radius * math.cos(angle), center_y + radius * math.sin(angle)))
        flat_points = [coord for point in points for coord in point]
        pdb.gimp_image_select_polygon(image, CHANNEL_OP_REPLACE, len(flat_points), flat_points)

    # Fill based on fill_type
    if fill_type == FillOptions.FOREGROUND:
        pdb.gimp_edit_fill(newLayer, FOREGROUND_FILL)
    elif fill_type == FillOptions.BACKGROUND:
        pdb.gimp_edit_fill(newLayer, BACKGROUND_FILL)    
    else:
        pdb.gimp_context_set_foreground(fill_color)
        pdb.gimp_edit_fill(newLayer, FOREGROUND_FILL)

    # Draw outline if required
    if outline and outline_size > 0:
        pdb.gimp_context_set_foreground(outline_color)  # Set outline color

        # Apply feathering if specified
        if feather_amount > 0:
            pdb.gimp_selection_feather(image, feather_amount)

        # Stroke the selection to create the outline
        pdb.gimp_edit_stroke(newLayer)  # Stroke the newLayer instead of drawable

    # Optionally, clear the selection again after drawing if necessary
    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_context_pop()  # Restore the previous context

    pdb.gimp_displays_flush()


register(
    "python_fu_draw_shape",
    "Draw Shape",
    "Draws shapes with customization options.",
    "Your Name",
    "Your Name",
    "2024",
    "<Image>/Filters/Shapes/Draw Shape...",
    "RGB*, GRAY*",
    [],
    [],
    show_dialog)

main()
