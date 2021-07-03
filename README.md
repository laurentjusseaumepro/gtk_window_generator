# gtk_window_generator
Use a JSON file to describe the widget and their hierarchy
```json
{
  "type": "object",
  "properties": {
    "id": {
      "description" : "Name of the widget",
      "type" : "string"
    },
    "type" : {
      "description" : "Type of the widget. Allowed values are : gtk_hor_box, gtk_ver_box, gtk_label, gtk_entry, gtk_label, gtk_scrolled_window, gtk_check_button and gtk_button",
      "type" : "string"
    },
    "text" : {
      "description" : "Text to write in the widget at creation time",
      "type" : "string"
    },
    "getter" : {
      "description" : "Indicates if a getter must be implemented for the widget. Default is false",
      "type" : "boolean"
    },
    "setter" : {
      "description" : "Indicates if a setter must be implemented for the widget. Default is false",
      "type" : "boolean"
    },
    "on_clicked" : {
      "description" : "Name of the callback invoked when widget is clicked",
      "type" : "string"
    },
    "children" : {
      "description" : "Array of children widgets",
      "type" : "array",
      "items" : {
        "type" : "object"
      }
    },
    "required": [
      "id",
      "type"
    ]
  }
}
```