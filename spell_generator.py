import tkinter as tk
from tkinter import ttk, filedialog
import os
import sys
import glob
import json
from collections import defaultdict
linked_data = defaultdict(dict)
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse


lsx_data = {}
xml_data = {}
txt_data = {}

# Linking an example XML data
uuid = 'some-uuid-from-xml'
linked_data[uuid]['xml_data'] = {'name': 'some_name', 'roottemplate': 'some_root_template'}

# Linking an example LSX data
uuid = 'some-uuid-from-lsx'
linked_data[uuid]['lsx_data'] = {'attribute_id': 'some_id', 'type': 'some_type'}


def debug_print(message):
    if DEBUG_MODE:  # Set DEBUG_MODE to True when you want to enable debugging
        print("DEBUG:", message)

class Translation:
    def __init__(self, content_uid, value):
        self.content_uid = content_uid
        self.value = value 

# New Dictionary to store Translation objects
TranslationLookup = {}

# Enable or disable debug mode
DEBUG_MODE = True

# Get the directory where this script is located
script_dir = os.path.dirname(__file__)
config_path = os.path.join(script_dir, 'config.json')

# Load configuration from JSON file
with open(config_path, 'r') as f:
    config = json.load(f)
    
# Function to select a folder through the file dialog
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected


#Find all xml make a book
# Function to find .xml and .lsx files
def parse_files(directory):
    all_files = find_files(directory)
    for file in all_files:
        if file.endswith('.xml'):
            parse_xml_file(file)
    load_translations()  # Load translations after parsing XML files

    #parse lsx file had to use different function
def parse_lsx_file(lsx_file_path):
    tree = ET.parse(lsx_file_path)
    root = tree.getroot()
    
    # XPath: Find all <attribute> elements nested under <node> that are within <region id="Templates">
    for attribute in root.findall('.//region[@id="Templates"]//node//attribute'):
        attribute_id = attribute.attrib.get('id', None)
        attribute_type = attribute.attrib.get('type', None)
        attribute_value = attribute.attrib.get('value', None)

        # Do something with these attributes, like storing them in a dictionary
    
    # Adding a new attribute element to the first <node> under <region id="Templates">
    target_node = root.find('.//region[@id="Templates"]//node')
    if target_node is not None:
        new_attribute = ET.SubElement(target_node, 'attribute')
        new_attribute.set("id", "YourIDHere")
        new_attribute.set("type", "YourTypeHere")
        new_attribute.set("value", "YourValueHere")
        
    lsx_data[attribute_id] = {
        'type': attribute_type,
        'value': attribute_value
    }

    
    # Saving the modified XML back to file
    tree.write(lsx_file_path)
    
def parse_txt_file(txt_file_path):
    entries = []
    with open(txt_file_path, 'r') as f:
        entry = {}
        for line in f:
            line = line.strip()
            if line.startswith("new entry"):
                if entry:
                    entries.append(entry)
                entry = {"entry_name": line.split('"')[1]}
            elif line.startswith("type") or line.startswith("using") or line.startswith("data"):
                parts = line.split('"')
                key = parts[0].strip()
                value = parts[1]
                entry[key] = value

        if entry:
            entries.append(entry)
            txt_data[entry["entry_name"]] = entry
    
    # Do something with the entries, like storing them in a database
    
    # Adding a new entry as an example
    new_entry = {
        "entry_name": "YourNewEntry",
        "type": "YourType",
        "data": "YourData"
    }
    entries.append(new_entry)
    
    # Saving the modified TXT back to file
    with open(txt_file_path, 'w') as f:
        for entry in entries:
            f.write(f'new entry "{entry["entry_name"]}"\n')
            for key, value in entry.items():
                if key != "entry_name":
                    f.write(f'{key} "{value}"\n')


# GameObject class uuid name display name etc
class GameObject:
    def __init__(self, uuid=None, name=None, display_name=None, mapkey=None, roottemplate=None, icon=None, description=None):
        self.uuid = uuid
        self.name = name
        self.display_name = display_name
        self.mapkey = mapkey
        self.roottemplate = roottemplate
        self.icon = icon  # New attribute to hold icon names
        self.description = description  # New attribute to hold descriptions
        self.children = []
        self.linked_objects = []  # new attribute to store linked GameObjects


# Update your StatDefinitionRepository class to include a method for linking
class StatDefinitionRepository:
    def __init__(self):
        self.definitions = defaultdict(list)

    def link_game_object(self, game_object):
        key = (game_object.name, game_object.display_name, game_object.mapkey, game_object.roottemplate, game_object.icon, game_object.description)
        self.definitions[key].append(game_object)
        
    def link_game_objects(self):
        for uuid, game_object in uuid_mapping.items():
            self.link_game_object(game_object)



# Add these new functions
def load_linking_rules():
    try:
        with open("linking_rules.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_linking_rules():
    with open("linking_rules.json", "w") as f:
        json.dump(linking_rules, f, indent=4)

# Function to load and save linking rules
def manage_linking_rules():
    global linking_rules
    # Logic to load and save linking rules
    # For demonstration, let's reload them (you would normally have some UI here to edit them)
    linking_rules = load_linking_rules()
    

# Initialize linking_rules globally
linking_rules = load_linking_rules()

# Function to select and parse game files
def select_and_parse_game_files():
    global shared_dir  # Declare shared_dir as global
    shared_dir = filedialog.askdirectory()  # Use a GUI to ask the user for the main directory
    xml_files = find_files(shared_dir, '.xml')
    lsx_files = find_files(shared_dir, '.lsx')
    txt_files = find_files(shared_dir, '.txt')
    # Now xml_files, lsx_files, and txt_files contain the paths to all your XML, LSX, and TXT files

    # Determine the directory where this script or executable is located
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)  # For compiled .exe
    else:
        script_dir = os.path.dirname(__file__)  # For Python script

    # Check if translation files exist
    translation_file_path = os.path.join(script_dir, 'translationFileConverted.xml')
    
    if os.path.exists(translation_file_path):
        # If they do, load translations
        load_translations()
    else:
        # If they don't, create an editable template (or skip)
        create_or_skip_translation_template()

# Function to create an editable translation template or skip
def create_or_skip_translation_template():
    # Implement the code to create a template or skip
    print("Translation files not found. Creating an editable template (or skipping).")
        
# Function to create an editable translation template or skip
def create_or_skip_translation_template():
    # This is a stub function; you can implement the code to create a template or skip
    # For example, you could create a new XML file with some default translations
    # Or you could show a message to the user asking if they want to create a template
    print("Translation files not found. Creating an editable template (or skipping).")

uuid_mapping = defaultdict(GameObject)    

# Modify your existing parse_xml_file function
def parse_xml_file(xml_file):
    tree = parse(xml_file)
    root = tree.getroot()
    
    for element in root.findall('.//YourXPathHere'):
        uuid = element.attrib.get('UUIDAttributeName', None)
        name = element.attrib.get('NameAttributeName', None)
        display_name = element.attrib.get('DisplayNameAttributeName', None)
        mapkey = element.attrib.get('MapKeyAttributeName', None)
        roottemplate = element.attrib.get('RootTemplateAttributeName', None)
        icon = element.attrib.get('IconAttributeName', None)
        description = element.attrib.get('DescriptionAttributeName', None)
        
        game_object = GameObject(uuid, name, display_name, mapkey, roottemplate, icon, description)
        uuid_mapping[uuid] = game_object
        
    xml_data[uuid] = {
        'name': name,
        'display_name': display_name,
        'mapkey': mapkey,
        'roottemplate': roottemplate,
        'icon': icon,
        'description': description
    }   

# New function to link UUIDs
def link_uuids(stat_repo):
    for uuid, game_object in uuid_mapping.items():
        # Step 1: Update the display_name for each game_object
        game_object.display_name = uuid_mapping.get(game_object.uuid, "Unknown UUID: " + game_object.uuid).display_name

        # Step 2: Link this game_object with stat_repo
        stat_repo.link_game_object(game_object)

def save_linking_rules():
    with open("linking_rules.json", "w") as f:
        json.dump(linking_rules, f, indent=4)

##Save object organize and used 


#UUID Parser translator
def load_uuid_mapping():
    uuid_to_text = {}
    try:
        xml_file_path = config.get('xml_file_path', 'English/Localization/English/english.xml')
        tree = ET.parse(xml_file_path)
        root = tree.getroot()  # Add this line; it seems you missed defining 'root'
        for content in root.findall('content'):
            uuid = content.get('contentuid')
            text = content.text
            uuid_to_text[uuid] = text
    except Exception as e:
        debug_print(f"Error loading UUID mapping: {e}")  # Debug print statement
        
    debug_print(list(uuid_to_text.items())[:5])  # Debug print statement
    return uuid_to_text

def load_translations():
    try:
        xml_file_path = config.get('translation_file_path', 'path/to/your/translationFileConverted.xml')
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for content in root.findall('content'):  
            content_uid = content.get('contentuid')
            value = content.text
            TranslationLookup[content_uid] = Translation(content_uid, value)
    except Exception as e:
        debug_print(f"Error loading translations: {e}")



def uuid_to_text(uuid, uuid_mapping):
    # Extract the core UUID part before any semicolon
    core_uuid = uuid.split(";")[0]
    translated_text = uuid_mapping.get(core_uuid, f"Unknown UUID: {uuid}")
    print(f"Translating UUID {uuid} to {translated_text}")  # Debugging line
    return translated_text


def text_to_uuid(text, uuid_mapping):
    for uuid, txt in uuid_mapping.items():
        if txt == text:
            return uuid
    return "Unknown Text"

# Function to find all files in a directory and its sub-directories
def find_files(directory, extension):
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(directory) for f in filenames if f.endswith(extension)]


def select_xml_file():
    xml_file_path = filedialog.askopenfilename(title="Select english.xml", filetypes=[("XML files", "*.xml")])
    if xml_file_path:
        config['xml_file_path'] = xml_file_path
        save_config()  # Function to save the updated config to a file 

# Function to load directory paths from config.json
def load_config():
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"shared_dir": "", "shared_dev_dir": "", "output_dir": ""}


#uuid_mapping = load_uuid_mapping()

# Load uuid_mapping globally
uuid_mapping = load_uuid_mapping()

# Initialize output_dir globally
output_dir = config.get('output_dir', "")

# Initialize directory variables
shared_dir = ""
shared_dev_dir = ""
output_dir = ""

# Load config and update directory variables
config = load_config()
shared_dir = config.get('shared_dir', "")
shared_dev_dir = config.get('shared_dev_dir', "")
output_dir = config.get('output_dir', "")

# Function to parse spell properties from a spell file
def parse_spell_properties(file_path):
    properties = set()
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip().startswith('data') and 'SpellProperties' in line:
                    parts = line.split('"')
                    if len(parts) > 3:
                        properties.add(parts[3])
    except Exception as e:
        print(f"An error occurred while parsing {file_path}: {e}")
    return properties

# Function to save directory paths to config.json
def save_config(shared_dir, shared_dev_dir, output_dir):
    config = {'shared_dir': shared_dir, 'shared_dev_dir': shared_dev_dir, 'output_dir': output_dir}
    with open(config_path, "w") as f:
        json.dump(config, f)

# Define attribute names that should contain UUIDs make this editable in the feature in config
uuid_attributes = {'DisplayName', 'SpellAnimation', 'Description', 'ExtraDescription', 'ShortDescription'}

# Enhanced function to parse all spell attributes
def parse_all_spell_attributes(file_path, uuid_mapping):
    attributes = defaultdict(set)
    uuid_regex = re.compile(r'\bh[0-9a-fg]{32};\d\b', re.IGNORECASE)  # Updated pattern

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip().startswith('data'):
                    parts = line.split('"')
                    if len(parts) > 3:
                        attr_name = parts[1]
                        attr_value = parts[3]
                        # Translate UUID to text if it matches UUID pattern
                        if uuid_regex.match(attr_value):
                            translated_value = uuid_to_text(attr_value, uuid_mapping)
                        else:
                            translated_value = attr_value
                        attributes[attr_name].add(translated_value)
    except Exception as e:
        print(f"An error occurred while parsing {file_path}: {e}")
    return attributes


# Example usage
# attributes = parse_all_spell_attributes("path/to/your/Spell_Projectile.txt")


# Function to update the listbox based on the selected spell type
def update_spell_properties(event=None):
    selected_type = spell_type_combo.get()
    properties = spell_attributes_dict.get(selected_type, {}).get("SpellProperties", set())
    spell_properties_listbox.delete(0, tk.END)
    for prop in properties:
        spell_properties_listbox.insert(tk.END, prop)

# Function to update spell_attributes_dict based on the selected directories
def update_spell_attributes_dict():
    global spell_attributes_dict
    spell_attributes_dict = {}
    spell_types = ["Projectile", "ProjectileStrike", "Rush", "Shout", "Target", "Teleportation", "Throw", "Wall", "Zone"]
    for spell_type in spell_types:
        for directory in [shared_dir, shared_dev_dir]:
            file_path = os.path.join(directory, f"Spell_{spell_type}.txt")
            if os.path.exists(file_path):
                attributes = parse_all_spell_attributes(file_path, uuid_mapping)  # <-- Added uuid_mapping here
                if spell_type not in spell_attributes_dict:
                    spell_attributes_dict[spell_type] = defaultdict(set)
                for attr, values in attributes.items():
                    spell_attributes_dict[spell_type][attr].update(values)



def generate_spell():
    selected_type = spell_type_combo.get()
    spell_name = spell_name_entry.get()

    # Step 1: Collect attribute values
    attribute_values = {}
    for attr, widget in attribute_widgets.items():
        value = widget[1].get()
        attribute_values[attr] = value

    # Step 2: Translate text to UUID if necessary
    for attr, value in attribute_values.items():
        uuid_value = text_to_uuid(value, uuid_mapping)  # Assuming uuid_mapping is globally available
        if uuid_value != "Unknown Text":
            attribute_values[attr] = uuid_value

    # Step 3: Generate file content
    file_content = []
    file_content.append(f"Spell Name: {spell_name}")
    file_content.append(f"Spell Type: {selected_type}")
    for attr, value in attribute_values.items():
        file_content.append(f'data "{attr}" "{value}"')

    file_content_str = "\n".join(file_content)

    # Step 4: Save to File
    output_file_path = os.path.join(output_dir, f"{spell_name}.txt")  # Assuming output_dir is globally available
    with open(output_file_path, "w") as f:
        f.write(file_content_str)

    print(f"Spell file generated at {output_file_path}")


# Update spell_attributes_dict initially
update_spell_attributes_dict()

# A dictionary to hold the dynamically generated widgets
attribute_widgets = {}

def load_attribute_widgets(attributes):
    global attribute_widgets
    attribute_widgets.clear()
    row_num = 6  # Starting row number in the grid for attribute widgets
    for attr, values in attributes.items():
        lbl = tk.Label(root, text=f"{attr}:")
        lbl.grid(row=row_num, column=0)
        if values:
            combo = ttk.Combobox(root, values=list(values))
            combo.grid(row=row_num, column=1)
        else:
            entry = tk.Entry(root)
            entry.grid(row=row_num, column=1)
        attribute_widgets[attr] = (lbl, combo if values else entry)
        row_num += 1
        
def select_xml_file():
    xml_file_path = filedialog.askopenfilename(title="Select english.xml", filetypes=[("XML files", "*.xml")])
    if xml_file_path:
        config['xml_file_path'] = xml_file_path
        save_config()

#Saveconfig
def save_config():
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

# Function to save data to a JSON file
# Function to save data to a JSON file
def save_to_json(output_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)


# Function to parse a custom XML file and return parsed data
def parse_custom_xml_file(xml_file):
    parsed_data = {}
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for content in root.findall('./content'):
        content_uid = content.attrib.get('contentuid', None)
        version = content.attrib.get('version', None)
        text = content.text
        parsed_data[content_uid] = {'version': version, 'text': text}

    return parsed_data



def main():
    load_translations()
    stat_repo = StatDefinitionRepository()
    link_uuids(stat_repo)  # You can add this if you want to link UUIDs right away
    save_to_json('output.json')  # Save all GameObjects to output.json
    save_combined_data_as_json()

    # Example XML, LSX, and TXT data dictionaries
    # Replace these with actual parsed data
    xml_data = {'key1': {'attr1': 'value1'}}
    lsx_data = {'key1': {'attr2': 'value2'}}
    txt_data = {'key1': {'attr3': 'value3'}}

    # Combine and save data
    save_combined_data_as_json(xml_data, lsx_data, txt_data)

    # The rest of your code
    link_uuids(stat_repo)
    parse_xml_file('path_to_xml_file')
    stat_repo.link_game_objects()

    
    # Link UUIDs
    link_uuids(stat_repo)
    parse_xml_file('path_to_xml_file')
    stat_repo.link_game_objects()
    
# Function to combine parsed data from XML, LSX, and TXT files
def combine_parsed_data(xml_data, lsx_data, txt_data):
    combined_data = {}
    for key, xml_entry in xml_data.items():
        combined_data[key] = {'XML': xml_entry}
        if key in lsx_data:
            combined_data[key]['LSX'] = lsx_data[key]
        if key in txt_data:
            combined_data[key]['TXT'] = txt_data[key]
    return combined_data



    save_to_json('output.json')

# Function to save combined data as JSON
def save_combined_data_as_json(xml_data, lsx_data, txt_data):
    combined_data = combine_parsed_data(xml_data, lsx_data, txt_data)
    save_to_json(combined_data, 'combined_data.json')

    
    # Save as JSON
    with open('combined_data.json', 'w') as f:
        json.dump(combined_data, f, indent=4)


# GUI code MAIN WINDOW
root = tk.Tk()
root.title("Spell Generator")

# Button to select and parse game files
tk.Button(root, text="Scan Entire Unpack Folder for UUID", command=select_and_parse_game_files).grid(row=9, column=0, padx=10, pady=5)

# Button to manage linking rules
tk.Button(root, text="Manage Linking Rules", command=manage_linking_rules).grid(row=10, column=0, padx=10, pady=5)

def select_folder():
    global shared_dir  # Declare shared_dir as global if it is
    shared_dir = filedialog.askdirectory()
    parse_files(shared_dir)  # Existing function to parse XML/LSX files
    load_translations()  # New function to load translations



# Function to select Shared directory
def select_shared_directory():
    global shared_dir
    shared_dir = filedialog.askdirectory()
    save_config(shared_dir, shared_dev_dir, output_dir)
    shared_dir_label.config(text=shared_dir)
    update_spell_attributes_dict()

# Function to select SharedDev directory
def select_shared_dev_directory():
    global shared_dev_dir
    shared_dev_dir = filedialog.askdirectory()
    save_config(shared_dir, shared_dev_dir, output_dir)
    shared_dev_dir_label.config(text=shared_dev_dir)
    update_spell_attributes_dict()

# Function to select output directory
def select_output_directory():
    global output_dir
    output_dir = filedialog.askdirectory()  
    save_config(shared_dir, shared_dev_dir, output_dir)
    output_dir_label.config(text=output_dir)

# Function to show attribute selection in a new window based on the selected spell type
def load_attributes():
    selected_type = spell_type_combo.get()  # Get the selected spell type
    attributes = spell_attributes_dict.get(selected_type, {})  # Get the attributes for the selected type
    debug_print(f"Loading attributes for type: {selected_type}")
    debug_print(f"Attributes found: {attributes}")

    
    # Create a new window
    new_window = tk.Toplevel(root)
    new_window.title(f"Select Attributes for {selected_type}")


    # Create a frame inside the new window
    frame = tk.Frame(new_window)
    frame.pack(fill=tk.BOTH, expand=1)
    uuid_to_text

    # Create a canvas inside the frame
    canvas = tk.Canvas(frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # Add a scrollbar to the canvas
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create another frame inside the canvas
    inner_frame = tk.Frame(canvas)

    # Add that new frame to a window in the canvas
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Populate the inner_frame with attribute selection widgets
    row_num = 0
    for attribute, values in attributes.items():
        tk.Label(inner_frame, text=f"{attribute}:").grid(row=row_num, column=0)
        
        # Translate UUIDs to text for certain attributes (if they are in the uuid_attributes set)
        if attribute in uuid_attributes:
            translated_values = [uuid_to_text(val, uuid_mapping) for val in values]
            ttk.Combobox(inner_frame, values=translated_values).grid(row=row_num, column=1)
        else:
            ttk.Combobox(inner_frame, values=list(values)).grid(row=row_num, column=1)
            
        row_num += 1

        

    # Add a submit button
    tk.Button(inner_frame, text="Submit", command=new_window.destroy).grid(row=row_num, columnspan=2)

# # Directory selection section #XML
btn_select_xml = tk.Button(root, text="Select english.xml", command=select_xml_file)
btn_select_xml.grid(row=0, column=0, sticky="w", padx=10, pady=5)
#Label button
tk.Label(root, text="Shared Dev Folder Location:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
tk.Label(root, text="Shared Folder Location:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
tk.Button(root, text="Shared Directory", command=select_shared_directory).grid(row=0, column=3, padx=10)
shared_dir_label = tk.Label(root, text=shared_dir)
shared_dir_label.grid(row=1, column=1, padx=10)
tk.Button(root, text="SharedDev Directory", command=select_shared_dev_directory).grid(row=0, column=2, padx=10)
shared_dev_dir_label = tk.Label(root, text=shared_dev_dir)
shared_dev_dir_label.grid(row=2, column=1, padx=10)
tk.Button(root, text="Output Directory", command=select_output_directory).grid(row=3, column=0, padx=10)
output_dir_label = tk.Label(root, text=output_dir)
output_dir_label.grid(row=3, column=1, padx=10)

# Widgets for spell name and type
tk.Label(root, text="New Spell Name:").grid(row=4, column=0, padx=10, pady=5)
spell_name_entry = tk.Entry(root)
spell_name_entry.grid(row=4, column=1, padx=10)

tk.Label(root, text="Spell Type:").grid(row=5, column=0, padx=10, pady=5)
spell_type_combo = ttk.Combobox(root, values=list(spell_attributes_dict.keys()))
spell_type_combo.grid(row=5, column=1, padx=10)
spell_type_combo.bind("<<ComboboxSelected>>", update_spell_properties)

# Button for loading spell attributes
tk.Button(root, text="Load Attributes", command=load_attributes).grid(row=6, column=0, padx=10, pady=5)

# Listbox for spell properties
tk.Label(root, text="Spell Properties:").grid(row=7, column=0, padx=10, pady=5)
spell_properties_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=10, width=50)
spell_properties_listbox.grid(row=7, column=1, padx=10)

# Generate spell file button
tk.Button(root, text="Generate Spell", command=generate_spell).grid(row=8, columnspan=3, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()

if __name__ == "__main__":
    main()
