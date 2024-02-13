password = '2025656990-254722460-3866451362025656990-254722460-386645136334454FADSFASDF45345'
import csv
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import subprocess
import os
import zipfile
import shutil
import copy
import base64
import pandas as pd

temp = 'temp'
working_directory = 'C:/Users/Josh/Desktop/MODS/Scripts/temp'
xls_file_path = 'C:/Users/Josh/Downloads/Rebalanced Mod.xlsx'
game_directory = 'D:/SteamLibrary/steamapps/common/They Are Billions'
filename = 'ZXRules.dat'
extract_name = 'ZXRules.dat'
unzipped_filename = 'output_xml_structure.xml'
zrulestartlocation = os.path.join(game_directory,filename)
zruleworklocation = f'{working_directory}/{extract_name}'
working_directory_file = f'{working_directory}/Modded'
temp_name = "UNZIPPED.dat"
temp_name_output = os.path.join(working_directory,temp_name)


replaces = [["AdvancedUnitCenter","EngineeringCenter",["PLACEHOLDER"]],
            ["MillIron","AdvancedWindmill",["PLACEHOLDER"]],
            ["MillWood","Windmill",["PLACEHOLDER"]],
            ["MachineGun","Wasp",["PLACEHOLDER"]],
            ["TrapStakes","WoodTraps",["PLACEHOLDER"]],
            ["TrapBlades","IronTraps",["PLACEHOLDER"]],
            ['"SoldierRegular','"Soldier',["Soldier_Shot","Soldier_Trained","Soldier_Die","Soldier_What","Soldier_Yes","Soldier_Attack"]],
            ['"SoldiersCenter','"SoldierRegularsCenter',["PLACEHOLDER"]],
            ['"SoldierRegularAttack"','"SoldierAttack"',["PLACEHOLDER"]],
            ["ThanatosExtraAttack","ThanatosRocket",["PLACEHOLDER"]],
            ['"ZombieGiantAttack"','"GiantAttack"',["PLACEHOLDER"]],
            ['"ZombieGiant"','"Giant"',["PLACEHOLDER"]],
            ["GiantDeath","ZombieGiantDeath",["PLACEHOLDER"]],
            ["ZombieHarpy","Harpy",["PLACEHOLDER"]],
            ['"BHZombieGiant"','"BHGiant"',["PLACEHOLDER"]],
            ['"ZombieGiantDeath"','"GiantDeath"',["PLACEHOLDER"]],
            ["ZombieVenom","Spitter",["PLACEHOLDER"]],
            ['"ZombieVenomAttack"','"SpitterAttack"',["PLACEHOLDER"]],
            ['"ZombieGiantRoar"','"GiantRoar"',["PLACEHOLDER"]],
            ['DeffensesLife','DefencesLife',["PLACEHOLDER"]],
            ['ResourceCollectionCellValue','ResourceGeneration',["PLACEHOLDER"]]
            ]

replaces_mayor = [["AdvancedUnitCenter","EngineeringCenter",["PLACEHOLDER"]],
                ["MillIron","AdvancedWindmill",["PLACEHOLDER"]],
                ["MillWood","Windmill",["PLACEHOLDER"]],
                ["MachineGun","Wasp",["PLACEHOLDER"]],
                ["TrapStakes","WoodTraps",["PLACEHOLDER"]],
                ["TrapBlades","IronTraps",["PLACEHOLDER"]],
                ['"SoldierRegular','"Soldier',["Soldier_Shot","Soldier_Trained","Soldier_Die","Soldier_What","Soldier_Yes","Soldier_Attack"]],
                ['"SoldiersCenter','"SoldierRegularsCenter',["PLACEHOLDER"]],
                ['SoldierRegular Life','Soldier Life',["PLACEHOLDER"]],
                ['"SoldierRegularAttack"','"SoldierAttack"',["PLACEHOLDER"]],
                ["ThanatosExtraAttack","ThanatosRocket",["PLACEHOLDER"]],
                ['"ZombieGiantAttack"','"GiantAttack"',["PLACEHOLDER"]],
                ['"ZombieGiant"','"Giant"',["PLACEHOLDER"]],
                ["GiantDeath","ZombieGiantDeath",["PLACEHOLDER"]],
                ["ZombieHarpy","Harpy",["PLACEHOLDER"]],
                ['"BHZombieGiant"','"BHGiant"',["PLACEHOLDER"]],
                ['"ZombieGiantDeath"','"GiantDeath"',["PLACEHOLDER"]],
                ["ZombieVenom","Spitter",["PLACEHOLDER"]],
                ['"ZombieVenomAttack"','"SpitterAttack"',["PLACEHOLDER"]],
                ['"ZombieGiantRoar"','"GiantRoar"',["PLACEHOLDER"]],
                ['DeffensesLife','DefencesLife',["PLACEHOLDER"]],
                ['ResourceCollectionCellValue','ResourceGeneration',["PLACEHOLDER"]]
                ]

empty_replaces = []

def unzip_file_with_7zip(input,output):
    sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'  # Adjust the path based on your installation
    try:
        command = [
            sevenzip_executable,
            'x',  # Extract files with full paths
            '-y',  # Assume Yes on all queries (overwrite files without prompting)
            f'-p{password}',  # Password for the archive
            f'-o{output}',  # Output directory
            input  # The path of the archive to extract
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting file '{input}': {e}")
        
def zip_files_with_7zip(input,output):
    # Set the path to the 7zip executable
    sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'# Adjust the path based on your installation
    command = [
        sevenzip_executable,
        'a',  
        '-tzip',
        '-mx9',
        '-p' + password,
        output, 
        input  ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error compressing file '{input}': {e}")

def format_cell_value(cell):
    """
    Format the cell value to handle numeric values correctly and replace new lines with semicolons:
    - Convert numeric values with no decimal part to integers.
    - Convert other values to string.
    """
    # Explicitly check for the string "None"
    if cell == "":
        return None
    elif pd.isnull(cell):
        return None  # Return None to indicate a null value explicitly
    elif isinstance(cell, float) and cell.is_integer():
        return str(int(cell))  # Convert to int to remove trailing .0
    else:
        # Convert other values to string, handling newline replacement if necessary
        return ";".join(str(cell).split('\n'))
                   
def read_excel_and_generate_xml(excel_path, sheet_name,replaces,extracolin = False):
    dictionary = Element('Dictionary', attrib={
        'name': "Rows",
        'keyType': "System.String, mscorlib",
        'valueType': "System.String[], mscorlib"
    })
    items = SubElement(dictionary, 'Items')

    # Read the Excel sheet into a pandas DataFrame
    df = pd.read_excel(excel_path, sheet_name=sheet_name,keep_default_na=False)

    for _, row in df.iterrows():
        item = SubElement(items, 'Item')
        first_cell_value = format_cell_value(row.iloc[0])
        # Ensure the first cell is processed correctly, including "None"
        if first_cell_value is None:
            SubElement(item, 'Simple', attrib={'value': "None"})
        else:
            SubElement(item, 'Simple', attrib={'value': first_cell_value})

        single_array = SubElement(item, 'SingleArray', attrib={'elementType': "System.String, mscorlib"})
        items_sub = SubElement(single_array, 'Items')
        
        # Ensure the first value is added again under the single array, including handling "None"
        if first_cell_value is None:
            SubElement(items_sub, 'Simple', attrib={'value': "None"})
        else:
            SubElement(items_sub, 'Simple', attrib={'value': first_cell_value})

        for cell in row[1:]:
            cell_value = format_cell_value(cell)
            if cell_value is None:
                SubElement(items_sub, 'Null')
            else:
                if extracolin:
                    cell_value = f"{cell_value};"
                    SubElement(items_sub, 'Simple', attrib={'value': cell_value})
                else:
                    if ";" in cell_value and not cell_value.endswith(";"):
                        cell_value = cell_value.replace(";","; ")
                    SubElement(items_sub, 'Simple', attrib={'value': cell_value})

    # Format XML
    rough_string = tostring(dictionary, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    lines = pretty_xml.splitlines()
    new_lines = []
    for line in lines:
        temp_string =str("              "+line+'\n').replace('/>', ' />')
        if ";" in temp_string and ';"' not in temp_string:
            last_quote_index = temp_string.rfind('"')
            if last_quote_index != -1:  # Ensure '"' was found
                temp_string = temp_string[:last_quote_index] + ';"' + temp_string[last_quote_index + 1:]
        if len(replaces) > 0:    
            for replace in replaces:
                found = False
                for exclusion in replace[2]:
                    if exclusion in temp_string:
                        found = True
                if not found:
                    temp_string = temp_string.replace(replace[1],replace[0])
        new_lines.append(temp_string)
        
        
    return new_lines

def read_file(input):
    with open(input, 'rb') as file:  # Open the file in binary mode
        content = file.read()
        
    # Check for UTF-8 BOM and remove it if present
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
        
    # Decode the content to utf-8
    content_decoded = content.decode('utf-8')
    
    # Split the content into lines
    lines = content_decoded.splitlines()
    
    # Optionally, you can add back the newline characters if needed
    lines = [line + '\n' for line in lines]
    
    return lines

def replace_and_insert(list1, list2, p, q):
    # Remove elements from list1 between indices p and q
    # Note: since slicing does not include the end index, we don't need to adjust q
    del list1[p:q]
    
    # Insert all elements from list2 at index p
    for i, item in enumerate(list2):
        list1.insert(p + i, item)
    
    return list1

def write_file(input,output):
    with open(output,'w', encoding='utf-8-sig') as f:
        for line in input:
            f.write(f'{line}')

unzip_file_with_7zip(zrulestartlocation,temp)

old_data        = read_file(temp_name_output)
entity_data     = read_excel_and_generate_xml(xls_file_path,"mod_ZXRules_Entities",replaces)
#mayor_data      = read_excel_and_generate_xml(xls_file_path,"ZXRules_Mayors",replaces_mayor)
#condition_data  = read_excel_and_generate_xml(xls_file_path,"mod_ZXRules_MapConditions",False,True)
command_data    = read_excel_and_generate_xml(xls_file_path,"mod_ZXRules_Commands",replaces)
#map_data        = read_excel_and_generate_xml(xls_file_path,"mod_ZXRules_MapThemes",empty_replaces)

new_data    = replace_and_insert(old_data,entity_data[1:],5000,20304)
#new_data    = replace_from_index(new_data,mayor_data[1:],21922)
new_data    = replace_and_insert(new_data,command_data[1:],256,4404)
#new_data    = replace_and_insert(new_data,map_data[1:],21548)




write_file(new_data,working_directory_file)  
zip_files_with_7zip(working_directory_file,filename)