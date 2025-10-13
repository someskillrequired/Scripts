import xml.etree.ElementTree as ET
import json
import os
import re

def parse_xml_to_dict(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    entity_dict = {}

    for dictionary in root.findall(".//Dictionary[@name='EntityTemplates']"):
        for item in dictionary.findall(".//Item"):
            id_value = None
            name_value = None
            id_category_value = None
            
            for simple in item.findall(".//Simple"):
                if simple.attrib.get('name') == 'ID' and id_value is None:
                    id_value = simple.attrib.get('value')
                elif simple.attrib.get('name') == 'Name' and name_value is None:
                    name_value = simple.attrib.get('value')
                elif simple.attrib.get('name') == 'IDCategory' and id_category_value is None:
                    id_category_value = simple.attrib.get('value')
            
            if id_value and name_value and id_value not in entity_dict:
                entity_dict[id_value] = {'Name': name_value, 'IDCategory': id_category_value}
    
    return entity_dict

def search_folder_for_entries(folder_path, entity_dict):
    for root_dir, _, files in os.walk(folder_path):
        for file in files:
            print(file)
            if file.endswith(".dxlevel"):
                file_path = os.path.join(root_dir, file)
                tree = ET.parse(file_path)
                root_element = tree.getroot()

                for key in entity_dict.keys():
                    
                    if 'template' in entity_dict[key]:
                        continue

                    for complex_elem in root_element.iterfind(".//Complex"):
                        id_template_elem = complex_elem.find(".//Simple[@name='IDTemplate']")
                        if id_template_elem is not None and id_template_elem.attrib.get('value') == key:
                            complex_text = ET.tostring(complex_elem, encoding='unicode', method='xml')

                            # Use regular expressions to replace Position and LastPosition values
                            complex_text = re.sub(r'(Position" value=")[^"]*(")', r'\1 0;0\2', complex_text)
                            complex_text = re.sub(r'(LastPosition" value=")[^"]*(")', r'\1 0;0\2', complex_text)

                            entity_dict[key]['template'] = complex_text
    keys_to_remove = [key for key, value in entity_dict.items() if 'template' not in value]
    for key in keys_to_remove:
        del entity_dict[key]

    return entity_dict

def write_dict_to_json(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

def alphabetize_dict_by_name(entity_dict):
    sorted_items = sorted(entity_dict.items(), key=lambda item: item[1]['Name'])
    return dict(sorted_items)

if __name__ == "__main__":
    xml_file = 'ZXGame_1.xml'  # Replace with your XML file path
    json_file = 'entity_dict2.json'  # Replace with your desired JSON output file path
    folder_path = r'D:\SteamLibrary\steamapps\common\TABOUTPUT\ZXGame_Data\Levels\Extracted'
    
    entity_dict          = parse_xml_to_dict(xml_file)
    sorted_entity_dict   = alphabetize_dict_by_name(entity_dict)
    enriched_entity_dict = search_folder_for_entries(folder_path, sorted_entity_dict)
    
    write_dict_to_json(enriched_entity_dict, json_file)
    print(f"Data successfully written to {json_file}")
