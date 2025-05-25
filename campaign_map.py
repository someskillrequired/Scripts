import subprocess
import sys
import os

r01_campaign_path = r"C:\Users\Josh\Desktop\TABSAT Project\MODS\Scripts\temp_data\256.dxlevel"
r01_custom_path   = r"C:\Users\Josh\Desktop\TABSAT Project\MODS\Scripts\temp_data\R01_custom.TABProject"
password   = "-1244806445-16584933701183625223"
mod_path = r"C:\Users\Josh\Desktop\TABSAT Project\MODS\Scripts\temp_data\modded"

arg = sys.argv[1]
sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'# Adjust the path based on your installation

def find_first_line_index(lines):
    for index, line in  enumerate(lines):
        if '<Collection name="Entities" elementType="DXVision.DXEntity, DXVision">' in line:
            return index
    raise ValueError("Not found")

def find_last_line_index(lines):
    for index, line in  enumerate(lines):
        if '<Collection name="ExtraEntities" elementType="DXVision.DXEntity, DXVision">' in line:
            index_holder = index
    return index_holder

def read_file(pass_file):
    with open(pass_file, "r") as file:
        file_lines = file.readlines()
    return file_lines

def write_file(pass_file,new_data):
    with open(pass_file,'w') as f:
        f.write("".join(new_data) + "\n")

def replace_section(target, source, target_start, target_end, source_start, source_end):
    return target[:target_start] + source[source_start:source_end] + target[target_end:]

def replace(file1,file2):
    file1_fline = find_first_line_index(file1)

    file2_fline = find_first_line_index(file2)
    file1_lline = find_last_line_index(file1)
    file2_lline = find_last_line_index(file2)
    
    new_lines   = replace_section(file1, file2, file1_fline, file1_lline,file2_fline,file2_lline)
    return new_lines

def unzip_file_with_7zip(password,input_location,output_location):
    # Split directory and filename
    folder_location, filename = os.path.split(input_location)
    #output_location = os.path.join(output_location,filename)
    try:
        command = [
            sevenzip_executable,
            'x',
            '-y',
            '-p' + password,
            input_location,
            f'-o{output_location}'
        ]
        subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'{input_location} Successfully Unzipped')
    except subprocess.CalledProcessError as e:
        print(f"Error extracting file '{input_location}': {e}")
    return os.path.join(output_location,filename)

def zip_files_with_7zip(password,input_locations,output_location):
    command = [
        sevenzip_executable,
        'a',  
        '-tzip',
        '-mx9',
        '-p' + password,
        output_location] + input_locations

    try:
        subprocess.run(command, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error compressing files '{input_locations}': {e}")

if __name__ == "__main__":

    unzipped_path_campaign      = unzip_file_with_7zip("",r01_campaign_path,mod_path)
    unzipped_path_custom        = unzip_file_with_7zip(password,r01_custom_path,mod_path)
    unzipped_path_custom        = r"C:\Users\Josh\Desktop\TABSAT Project\MODS\Scripts\temp_data\modded\Data"
    unzipped_path_custom_info  = r"C:\Users\Josh\Desktop\TABSAT Project\MODS\Scripts\temp_data\modded\Info"
    campaign_file               = read_file(unzipped_path_campaign)
    custom_file                 = read_file(unzipped_path_custom)
     
    if arg == "custom":
        new = replace(custom_file,campaign_file)
        write_file(unzipped_path_custom,new)
        zip_files_with_7zip(password,[unzipped_path_custom,unzipped_path_custom_info],r01_custom_path)
        
        
    elif arg == "campaign":
        new = replace(campaign_file,custom_file)
        write_file(unzipped_path_campaign,new)
        zip_files_with_7zip()
        
        

    