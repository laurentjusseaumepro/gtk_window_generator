#!/usr/bin/env python3
import json
import logging
import argparse

LABEL_PREFIX = "self."

known_gtk_types = {
    "gtk_hor_box"         : {"GTK" :"Gtk.Box", "name_in_constructor" : False},
    "gtk_ver_box"         : {"GTK" :"Gtk.VBox", "name_in_constructor" : False},
    "gtk_label"           : {"GTK" :"Gtk.Label", "name_in_constructor" : True},
    "gtk_entry"           : {"GTK" :"Gtk.Entry", "name_in_constructor" : False},
    "gtk_scrolled_window" : {"GTK" :"Gtk.ScrolledWindow", "name_in_constructor" : False},
    "gtk_check_button"    : {"GTK" :"Gtk.CheckButton", "name_in_constructor" : True},
    "gtk_button"          : {"GTK" :"Gtk.Button", "name_in_constructor" : True},
    "gtk_h_button_box"    : {"GTK" :"Gtk.HButtonBox", "name_in_constructor" : False},
    "gtk_v_button_box"    : {"GTK" :"Gtk.VButtonBox", "name_in_constructor" : False},
    "gtk_notebook"        : {"GTK" :"Gtk.Notebook", "name_in_constructor" : False}
    }

generated_code_widget = []
getter_list = []
setter_list = []
button_callbacks = dict()

def analyze_item(json_item, parent_label, parent_type) :
    logger.debug("analyzing item child of {0}".format(parent_label))
    l_json_item = None
    l_gtk_type = None
    has_getter = False
    has_setter = False
    label_text = ""
    label_type = None
    name_in_constructor = False
    on_clicked = None
    page_name = None

    for item in json_item:
        if item == "id":
            l_label = LABEL_PREFIX + json_item[item]
            logger.debug("label = {0}".format(l_label))
        elif item == "type":
            if json_item[item] in known_gtk_types:
                logger.debug("item {0} is a knwon type".format(json_item[item]))
                l_gtk_type = known_gtk_types[json_item[item]]["GTK"]
                label_type = json_item[item]
                name_in_constructor = known_gtk_types[json_item[item]]["name_in_constructor"]
            else:
              logger.debug("item {0} is an unknwon type".format(json_item[item]))
        elif item == "children":
            l_json_item = json_item[item]
        elif item == "text":
            label_text = json_item[item]
        elif item == "getter":
            has_getter = json_item[item]
        elif item == "setter":
            has_setter = json_item[item]
        elif item == "on_clicked":
            on_clicked = json_item[item]
        elif item == "page_name":
            page_name = json_item[item]
        else:
            logger.debug("item {0} is an unknwon type".format(item))
    
    if not l_gtk_type is None:
        logger.debug("adding code line")
        logger.debug("l_label={0}".format(l_label))
        logger.debug("l_gtk_type={0}".format(l_gtk_type))
        if name_in_constructor:
            code_line = l_label + " = " + l_gtk_type + "(\"" + label_text +"\")"
        else:
            code_line = l_label + " = " + l_gtk_type + "()"
        generated_code_widget.append(code_line)

        if label_text != "" and not name_in_constructor:
            code_line = l_label + ".set_text(\"" + label_text + " \")"
            generated_code_widget.append(code_line)

        if  not on_clicked is None:
            code_line = l_label + ".connect(\"clicked\", " + l_label + "_clicked)"
            generated_code_widget.append(code_line)
            button_callbacks[l_label] = on_clicked

        if parent_type == None:
            code_line = "self.add (" + l_label + ")"
        elif parent_type == "gtk_scrolled_window":
            code_line = parent_label + ".add_with_viewport(" + l_label + ")"
        elif parent_type == "gtk_notebook":
            generated_code_widget.append("label_title = Gtk.Label(\"" + page_name + "\")")
            code_line = parent_label + ".append_page(" + l_label + ", label_title)"
        else:
            code_line = parent_label + ".pack_start(" + l_label + ", True, True, 0)"
        
        generated_code_widget.append(code_line)
        if has_getter:
            getter_list.append(l_label)
        if has_setter:
            setter_list.append(l_label)

    if not l_json_item is None:
        if isinstance(l_json_item, list):
            logger.debug("it is an array")
            for item in l_json_item:
                analyze_item(item, l_label, label_type)
        else:
            analyze_item(l_json_item, l_label, label_type)

def write_getters(f):
    f.write('    # Getters \n')
    for label in getter_list:
        label_short = label.split(".")[1]
        f.write('    def get_' + label_short + '(self):\n')
        f.write('        return ' + label + '.get_text()\n')
        f.write('\n')

def write_setters(f):
    f.write('    # Setters \n')
    for label in setter_list:
        label_short = label.split(".")[1]
        f.write('    def set_' + label_short + '(self, value):\n')
        f.write('        ' + label + '.set_text(value)\n')
        f.write('\n')

def write_button_listeners(f):
    f.write('    # Listeners \n')
    for button in button_callbacks:
        f.write('    def ' + button.split('.')[1] + '_clicked(self, button):\n')
        f.write('        self.controller.' + button_callbacks[button] + '()\n')
        f.write('\n')

def main():
    # create console handler and set level to debug
    ch = logging.StreamHandler()

    # add ch to logger
    logger.addHandler(ch)

    # add argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="print debug info",
                        action="store_true")
    parser.add_argument('-f', '--file', dest="in_file", type=str, default="window.json",
                        help='JSON filename describing the widgets')
    parser.add_argument('-s', '--source', dest="source_python", type=str, default="head.py",
                        help='Python source file containing the first lines of code')
    parser.add_argument('-o', '--output', dest="out_file", type=str, default="MainWindow.py",
                        help='Generated file')
    args = parser.parse_args()

    # set verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # read JSON file
    try:
        with open(args.in_file, "r") as json_file:
            json_content = json.loads(json_file.read())
    except Exception as e:
        logger.error(e)
        return
    
    # read python source file
    try:
        with open(args.source_python, "r") as python_file:
            python_firt_lines = python_file.read()
    except Exception as e:
        logger.error(e)
        return

    # Analyze
    analyze_item(json_content,"", None)

    logger.debug("")
    for line in generated_code_widget:
        logger.debug(line)

    logger.debug(getter_list)
    logger.debug(setter_list)

    logger.debug(button_callbacks)

    # Generate python file
    with open(args.out_file, 'w') as dest_file:
        dest_file.write('"""\n')
        dest_file.write('File generated. Do not edit manually !!!\n')
        dest_file.write('Use script window_generator.py\n')
        dest_file.write('"""\n')
        dest_file.write('\n')

        # Copy header file
        for line in python_firt_lines:
            dest_file.write(line)

        # Add generated source
        dest_file.write('\n')
        for line in generated_code_widget:
            dest_file.write("        " + line + '\n')
        
        dest_file.write('\n')

        # Add getters, setters and listeners
        write_getters(dest_file)
        write_setters(dest_file)
        write_button_listeners(dest_file)

# create logger
logger = logging.getLogger('window_generator')
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    main()