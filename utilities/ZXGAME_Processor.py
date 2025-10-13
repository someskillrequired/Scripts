import xml.etree.ElementTree as ET
import re
import os
import subprocess

default_game_directory = r'D:\Steam\steamapps\common\They Are Billions'
default_sevenzip_executable = r'C:/Program Files/7-Zip/7z.exe'

# Precompile regex patterns for better performance
SIMPLE_PATTERN = re.compile(r'<Simple name="([^"]+)" value="([^"]+)"')
ID_PATTERN = re.compile(r'<Simple value="(\d+)"')
NAME_PATTERN = re.compile(r'<Simple name="Name" value="([^"]+)"')
FILE_PATTERN = re.compile(r'<Simple name="FileName" value="([^"]+)"')
IMAGE_FILE_PATTERN = re.compile(r'<Simple\s+name="FileName"[^>]*\svalue="([^"]+)"')
IMAGE_ATTR_PATTERN = re.compile(r'<Simple\s+name="([^"]+)"\s+value="([^"]+)"')

def check_string_match(level1_dict, match_string):
    for key, value in level1_dict.items():
        if value.get('string') == match_string:
            return key
    return None

class ZXGame_Parser():
    def __init__(self, game_directory, temp_directory):
        self.file_name = 'ZXGame.dxprj'
        self.file_name_unzipped = 'ZXGame.dxprj'
        self.file_name_modded = 'ZXGame_modded.dxprj'
        self.temp_directory = temp_directory
        self.file_path = os.path.join(game_directory, self.file_name)
        self.file_path_unzipped = os.path.join(temp_directory, self.file_name)
        self.file_path_unzipped_modded = os.path.join(temp_directory, self.file_name_modded)
        
        # Initialize all processing methods
        self.LevelZeroProcessing()
        self.LevelOneProcessing()
        self.LevelTwoProcessing()
        self.LevelThreeProcessing()
        self.LevelFourProcessing()
        self.LevelFiveProcessing()
        self.LevelSixProcessing()
        self.image_mapping()
        self.print_json()

    def unzip_file(self):
        pass
    
    def zip_file(self):
        pass    

    def save_file(self, image_dict):
        # Read the file with original line endings preserved
        with open(self.file_path_unzipped, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            print(lines[0])
        
        # We'll track how much each operation shifts subsequent line numbers
        line_shift = 0
        # Store operations sorted by original start line
        operations = []
        
        # Collect all operations first
        for item in image_dict.values():
            if 'Map_Details' not in item or 'Modified' not in item['Map_Details']:
                continue
                
            details = item['Map_Details']
            operations.append({
                'type': details['Modified'],
                'start': details['StartLine'],
                'end': details['EndLine'],
                'template': details.get('template', []),
                'content': details.get('content', [])
            })
        
        # Sort operations by start line (process earliest first)
        operations.sort(key=lambda x: x['start'])
        
        # Process each operation, adjusting for previous shifts
        for op in operations:
            adjusted_start = op['start'] + line_shift
            adjusted_end = op['end'] + line_shift
            
            if op['type'] == 'Deleted':
                # Verify the range is valid
                if 0 <= adjusted_start < len(lines) and 0 <= adjusted_end < len(lines):
                    del lines[adjusted_start:adjusted_end+1]
                    line_shift -= (op['end'] - op['start'] + 1)
            
            elif op['type'] == 'Moved':
                if 0 <= adjusted_start < len(lines) and 0 <= adjusted_end < len(lines):
                    # Ensure consistent line endings
                    template = [line.rstrip('\r\n') + '\n' for line in op['template']]
                    lines[adjusted_start:adjusted_end+1] = template
            
            elif op['type'] == 'Added':
                if 0 <= adjusted_start <= len(lines):
                    # Ensure consistent line endings
                    content = [line.rstrip('\r\n') + '\n' for line in op['content']]
                    lines[adjusted_start:adjusted_start] = content
                    line_shift += len(content)
        
        # Write the main file with original line endings
        with open(self.file_path_unzipped, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        return image_dict
    
    def LevelZeroProcessing(self):
        self.Reconquest_id = '4104776980463107687'
        self.Reconquest_sub_dicts = {
            'frames': '<Dictionary name="Frames" keyType="System.Int32, mscorlib" valueType="DXVision.DXProjectFrame, DXVision">',
            'objects': '<Dictionary name="Objects" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectObject, DXVision">'
        }
        
        self.Level1 = {
            'Categories': {'string': '    <Collection name="Categories" elementType="DXVision.DXProjectCategory, DXVision">\r\n'},
            'PencilColors': {'string': '    <Dictionary name="PencilColors" keyType="System.String, mscorlib" valueType="System.Drawing.Color, System.Drawing">\r\n'},
            'ImageGallery': {'string': '    <Dictionary name="ImageGallery" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectImage, DXVision">\r\n'},
            'Clips': {'string': '    <Dictionary name="Clips" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectClip, DXVision">\r\n'},
            'TextTemplates': {'string': '    <Dictionary name="TextTemplates" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectTextTemplate, DXVision">\r\n'},
            'Fonts': {'string': '    <Dictionary name="Fonts" keyType="System.String, mscorlib" valueType="System.Byte[], mscorlib">\r\n'},
            'GIFs': {'string': '    <Dictionary name="GIFs" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectGIF, DXVision">\r\n'},
            'Sprites': {'string': '    <Dictionary name="Sprites" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectSprite, DXVision">\r\n'},
            'AVIs': {'string': '    <Dictionary name="AVIs" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectAVI, DXVision">\r\n'},
            'EntityTemplates': {'string': '    <Dictionary name="EntityTemplates" keyType="System.UInt64, mscorlib" valueType="DXVision.DXEntityTemplate, DXVision">\r\n'},
            'Levels': {'string': '    <Dictionary name="Levels" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectLevel, DXVision">\r\n'}
        }
    
    def LevelOneProcessing(self):
        force = False
        if not os.path.exists(self.file_path_unzipped) or force == True:
            command = [
                default_sevenzip_executable,
                'x',
                '-y',
                f'-o{self.temp_directory}',
                self.file_path
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        line_count = 0
        with open(self.file_path_unzipped, 'rb') as file:
            for index, line in enumerate(file):
                line = line.decode('utf-8')
                match = check_string_match(self.Level1, line)
                
                if match:
                    self.Level1[match]['StartLine'] = index

                line_count += 1
        
        keys = list(self.Level1.keys())
        for i in range(len(keys) - 1, 0, -1):
            current_key = keys[i]
            previous_key = keys[i - 1]
            if 'StartLine' in self.Level1[current_key]:
                self.Level1[previous_key]['EndLine'] = self.Level1[current_key]['StartLine'] - 1
        
        if 'Levels' in self.Level1:
            self.Level1['Levels']['EndLine'] = line_count - 3

    def LevelTwoProcessing(self):
        start_line = self.Level1['Levels'].get('StartLine')
        end_line = self.Level1['Levels'].get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        with open(self.file_path_unzipped, 'rb') as file:
            relevant_lines = [line.decode('utf-8') for index, line in enumerate(file) 
                            if start_line <= index <= end_line]
        
        data_dict = {}
        current_item = None
        in_items = False

        for index, line in enumerate(relevant_lines):
            if not in_items and '<Items>' in line:
                in_items = True
                continue
            
            if in_items:
                if '<Item>' in line and current_item is None:
                    current_item = index
                    data_dict[current_item] = {'template': [line], 'StartLine': start_line + index}
                elif '</Item>' in line and current_item is not None:
                    data_dict[current_item]['template'].append(line)
                    data_dict[current_item]['EndLine'] = start_line + index
                    current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)
        
        self.Level1['Levels']['Level'] = {}
        for item in data_dict.values():
            for line in item['template']:
                match = FILE_PATTERN.search(line)
                if match:
                    file_name = match.group(1)
                    self.Level1['Levels']['Level'][file_name] = {
                        'template': item['template'],
                        'StartLine': item['StartLine'],
                        'EndLine': item['EndLine']
                    }
                    break
                            
    def LevelThreeProcessing(self):
        start_line = self.Level1['Clips'].get('StartLine')
        end_line = self.Level1['Clips'].get('EndLine')
        
        if start_line is None or end_line is None:
            print('here')
            return
        
        relevant_lines = []
        with open(self.file_path_unzipped, 'rb') as file:
            relevant_lines = [line.decode('utf-8') for index, line in enumerate(file) if start_line <= index <= end_line]
        
        self.Level1['Clips']['Data'] = {}
        data_dict = self.Level1['Clips']['Data']
        current_item = None
        item_count = 0
        in_items = False
        
        for index, line in enumerate(relevant_lines):
            if not in_items and '<Items>' in line:
                in_items = True
                continue
            
            if in_items:
                if '<Item>' in line and item_count == 0:
                    current_item = index
                    item_count += 1
                    data_dict[current_item] = {'template': [line], 'StartLine': start_line + index}
                elif '<Item>' in line:
                    data_dict[current_item]['template'].append(line)
                    item_count += 1
                elif '</Item>' in line:
                    item_count -= 1
                    if current_item is not None:
                        data_dict[current_item]['template'].append(line)
                        data_dict[current_item]['EndLine'] = start_line + index
                        if item_count == 0:
                            template_str = ''.join(data_dict[current_item]['template'])
                            id_match = ID_PATTERN.search(template_str)
                            if id_match:
                                simple_value_id = id_match.group(1)
                                data_dict[simple_value_id] = data_dict.pop(current_item)
                                data_dict[simple_value_id]['ID'] = simple_value_id
                            current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)

    def LevelFourProcessing(self):
        clip_data = self.Level1['Clips']['Data'].get(self.Reconquest_id)
        if not clip_data:
            return
            
        start_line = clip_data.get('StartLine')
        end_line = clip_data.get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        with open(self.file_path_unzipped, 'rb') as file:
            relevant_lines = [line.decode('utf-8') for index, line in enumerate(file) 
                            if start_line <= index <= end_line]
        
        clip_data['objects'] = {}
        data_dict = clip_data['objects']
        current_item = None
        item_count = 0
        in_objects = False
        
        for index, line in enumerate(relevant_lines):
            if not in_objects and self.Reconquest_sub_dicts['objects'] in line:
                in_objects = True
                continue
            
            if in_objects:
                if '<Item>' in line and item_count == 0:
                    current_item = index
                    item_count += 1
                    data_dict[current_item] = {'template': [line], 'StartLine': start_line + index}
                elif '<Item>' in line:
                    data_dict[current_item]['template'].append(line)
                    item_count += 1
                elif '</Item>' in line:
                    item_count -= 1
                    if current_item is not None:
                        data_dict[current_item]['template'].append(line)
                        data_dict[current_item]['EndLine'] = start_line + index
                        if item_count == 0:
                            template_str = ''.join(data_dict[current_item]['template'])
                            name_match = NAME_PATTERN.search(template_str)
                            id_match = ID_PATTERN.search(template_str)
                            if name_match:
                                name_value = name_match.group(1)
                                data_dict[name_value] = data_dict.pop(current_item)
                                data_dict[name_value]['Name'] = name_value
                            if id_match:
                                id_value = id_match.group(1)
                                data_dict[name_value]['ID'] = id_value
                            current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)

    def LevelFiveProcessing(self):
        clip_data = self.Level1['Clips']['Data'].get(self.Reconquest_id)
        if not clip_data:
            return
            
        start_line = clip_data.get('StartLine')
        end_line = clip_data.get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        with open(self.file_path_unzipped, 'rb') as file:
            relevant_lines = [line.decode('utf-8') for index, line in enumerate(file) 
                            if start_line <= index <= end_line]
        
        clip_data['frames'] = {}
        data_dict = clip_data['frames']
        current_item = None
        item_count = 0
        in_frames = False
        
        for index, line in enumerate(relevant_lines):
            if not in_frames and '<Dictionary name="ObjectInstances"' in line:
                in_frames = True
                continue
            elif self.Reconquest_sub_dicts['objects'] in line:
                break
            
            if in_frames:
                if '<Item>' in line and item_count == 0:
                    current_item = index
                    item_count += 1
                    data_dict[current_item] = {'template': [line], 'StartLine': start_line + index}
                elif '<Item>' in line:
                    data_dict[current_item]['template'].append(line)
                    item_count += 1
                elif '</Item>' in line:
                    item_count -= 1
                    if current_item is not None:
                        data_dict[current_item]['template'].append(line)
                        data_dict[current_item]['EndLine'] = start_line + index
                        if item_count == 0:
                            template_str = ''.join(data_dict[current_item]['template'])
                            id_match = ID_PATTERN.search(template_str)
                            if id_match:
                                id_value = id_match.group(1)
                                data_dict[current_item]['ID'] = id_value
                            current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)

        new_data_dict = {value['ID']: value for value in data_dict.values()}
        clip_data['frames'] = new_data_dict

    def LevelSixProcessing(self):
        clip_data = self.Level1['Clips']['Data'].get(self.Reconquest_id)
        if not clip_data:
            return
            
        # Process frames
        for item in clip_data['frames'].values():
            for line in item['template']:
                for name, value in SIMPLE_PATTERN.findall(line):
                    item[name] = value
        
        # Process objects
        for item in clip_data['objects'].values():
            if isinstance(item, dict):  # Skip if it's not a dictionary (like template strings)
                for line in item['template']:
                    for name, value in SIMPLE_PATTERN.findall(line):
                        item[name] = value

    def image_mapping(self):
        with open(self.file_path_unzipped, 'rb') as file:
            lines = [line.decode('utf-8') for line in file]

        image_dict = {}
        current_image = None
        
        for line in lines:
            if '<Complex name="Image" type="DXVision.DXImageFile, DXVision">' in line:
                current_image = None
            elif current_image is None and '<Simple name="FileName"' in line:
                match = IMAGE_FILE_PATTERN.search(line)
                if match:
                    current_image = match.group(1)
                    image_dict[current_image] = {}
            elif current_image is not None:
                submatch = IMAGE_ATTR_PATTERN.search(line)
                if submatch:
                    image_dict[current_image][submatch.group(1)] = submatch.group(2)

        reversed_image_dict = {v['ID']: k for k, v in image_dict.items() if 'ID' in v}

        self.Level1['my_image_dict'] = image_dict
        self.Level1['my_reversed_dict'] = reversed_image_dict

        return image_dict
    
    def print_json(self):
        pass
        # with open('ZXGame.json', 'w', encoding='utf-8') as json_file:
        #     json.dump(self.Level1, json_file, ensure_ascii=False, indent=2)