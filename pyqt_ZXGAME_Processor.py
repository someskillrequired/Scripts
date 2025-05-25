import xml.etree.ElementTree as ET
import json
import re



def check_string_match(level1_dict, match_string):
    return next((key for key, value in level1_dict.items() if value.get('string') == match_string), None)

class ZXGame_Parser():
    def __init__(self,game_directory,temp_directory):
        self.file_name          = 'ZXGame.dxprj'
        self.file_name_unzipped = 'ZXGame.dxprj'
        self.file_name_modded   = 'ZXGame_modded.dxprj'
        
        self.file_path          = game_directory + '//' + self.file_name
        self.file_path_unzipped = temp_directory + '//' + self.file_name
        self.file_path_unzipped_modded = temp_directory + '//' +  self.file_name_modded 
        self.LevelZeroProcessing()
        
        self.LevelOneProcessing()
        #Level 2 pull 'Levels' Data
        self.LevelTwoProcessing()
        #Level 3 initial pull of 'clips' data
        self.LevelThreeProcessing()
        #level 4 subpull of 'objects' from clips data
        self.LevelFourProcessing()
        #level 5 subpull of 'frames' from clips data
        self.LevelFiveProcessing()
        #level 6 processing looking through the frames clip data and pulling out the following attributes sizex sizey 
        self.LevelSixProcessing()
        
    def unzip_file(self):
        pass
    
    def zip_file(self):
        pass    

    def update_file(self,image_dict):
        with open(self.file_path_unzipped, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for item in image_dict:
            if image_dict[item]['Map_Details'].get('MODIFIED',False) == True:
                image_dict[item]['Map_Details']['MODIFIED'] = False
                temp_item = image_dict[item]['Map_Details']
                lines[temp_item['StartLine']:temp_item['EndLine']+1] = temp_item['template']
        
        with open(self.file_path_unzipped_modded, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        
        return image_dict
    
    def LevelZeroProcessing(self):
        self.Reconquest_id = '4104776980463107687'

        self.Reconquest_sub_dicts = {'frames':'<Dictionary name="Frames" keyType="System.Int32, mscorlib" valueType="DXVision.DXProjectFrame, DXVision">',
                                     'objects':'<Dictionary name="Objects" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectObject, DXVision">'}
        
        
        self.Level1 =   {
                        'Categories'      : {'string': '    <Collection name="Categories" elementType="DXVision.DXProjectCategory, DXVision">\r\n'                                       },
                        'PencilColors'    : {'string': '    <Dictionary name="PencilColors" keyType="System.String, mscorlib" valueType="System.Drawing.Color, System.Drawing">\r\n'     },
                        'ImageGallery'    : {'string': '    <Dictionary name="ImageGallery" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectImage, DXVision">\r\n'        },
                        'Clips'           : {'string': '    <Dictionary name="Clips" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectClip, DXVision">\r\n'                },
                        'TextTemplates'   : {'string': '    <Dictionary name="TextTemplates" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectTextTemplate, DXVision">\r\n'},
                        'Fonts'           : {'string': '    <Dictionary name="Fonts" keyType="System.String, mscorlib" valueType="System.Byte[], mscorlib">\r\n'                         },
                        'GIFs'            : {'string': '    <Dictionary name="GIFs" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectGIF, DXVision">\r\n'                  },
                        'Sprites'         : {'string': '    <Dictionary name="Sprites" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectSprite, DXVision">\r\n'            },
                        'AVIs'            : {'string': '    <Dictionary name="AVIs" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectAVI, DXVision">\r\n'                  },
                        'EntityTemplates' : {'string': '    <Dictionary name="EntityTemplates" keyType="System.UInt64, mscorlib" valueType="DXVision.DXEntityTemplate, DXVision">\r\n'   },
                        'Levels'          : {'string': '    <Dictionary name="Levels" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectLevel, DXVision">\r\n'              }
                    }
    
    def LevelOneProcessing(self):
        line_count = 0
        
        # Pull all lines for dictionary starts and count total lines
        with open(self.file_path_unzipped, 'rb') as file:
            for index, line in enumerate(file):
                line = line.decode('utf-8')
                match = check_string_match(self.Level1, line)
                if match is not None:
                    self.Level1[match]['StartLine'] = index
                line_count += 1
        
        # Use the next key in the list to find where you ended
        keys = list(self.Level1.keys())
        for i in range(len(keys) - 1, 0, -1):
            current_key = keys[i]
            previous_key = keys[i - 1]
            if 'StartLine' in self.Level1[current_key]:
                self.Level1[previous_key]['EndLine'] = self.Level1[current_key]['StartLine'] - 1
        
        # Update the last item ('Levels') with the end line
        if 'Levels' in self.Level1:
            self.Level1['Levels']['EndLine'] = line_count - 3

    def LevelTwoProcessing(self):
        # Read only the relevant lines for Levels
        start_line = self.Level1['Levels'].get('StartLine')
        end_line = self.Level1['Levels'].get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        
        with open(self.file_path_unzipped, 'rb') as file:
            for index, line in enumerate(file):
                if start_line <= index <= end_line:
                    relevant_lines.append(line.decode('utf-8'))
        
        start = False
        data_dict = {}
        current_item = None

        for index, line in enumerate(relevant_lines):
            if not start:
                if '<Items>' in line:
                    start = True
            else:
                if '<Item>' in line:
                    current_item = index
                    data_dict[current_item] = {'template': [line], 'StartLine': start_line + index}
                elif '</Item>' in line:
                    if current_item is not None:
                        data_dict[current_item]['template'].append(line)
                        data_dict[current_item]['EndLine'] = start_line + index
                        current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)
        
        pattern = r'<Simple name="FileName" value="([^"]+)"'
        self.Level1['Levels']['Level'] = {}

        # Insert new dict into level dict
        for item in data_dict.keys():
            for line in data_dict[item]['template']:
                match = re.search(pattern, line)
                if match:
                    file_name = match.group(1)
                    self.Level1['Levels']['Level'][file_name] = {
                        'template': data_dict[item]['template'],
                        'StartLine': data_dict[item]['StartLine'],
                        'EndLine': data_dict[item]['EndLine']}
                            
    def LevelThreeProcessing(self):
        start_line = self.Level1['Clips'].get('StartLine')
        end_line = self.Level1['Clips'].get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        
        with open(self.file_path_unzipped, 'rb') as file:
            for index, line in enumerate(file):
                if start_line <= index <= end_line:
                    relevant_lines.append(line.decode('utf-8'))
        
        start = False
        self.Level1['Clips']['Data'] = {}
        data_dict = self.Level1['Clips']['Data']
        current_item = None
        item_count = 0
        first = True
        
        # Regex pattern to extract the first Simple value ID
        id_pattern = re.compile(r'<Simple value="(\d+)"')
        
        for index, line in enumerate(relevant_lines):
            if not start:
                if '<Item>' in line:
                    start = True
            else:
                if '<Item>' in line and (item_count == 0 or first == True):
                    if first == True:
                        first = False
                        item_count += 1
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
                            # Extract the first Simple value ID within the Item
                            template_str = ''.join(data_dict[current_item]['template'])
                            id_match = id_pattern.search(template_str)
                            if id_match:
                                simple_value_id = id_match.group(1)
                                # Move the data to a new key based on simple_value_id
                                data_dict[simple_value_id] = data_dict.pop(current_item)
                                data_dict[simple_value_id]['ID'] = simple_value_id
                            current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)

    def LevelFourProcessing(self):
        # Retrieve the start and end lines for the specific ID
        start_line = self.Level1['Clips']['Data']['4104776980463107687'].get('StartLine')
        end_line = self.Level1['Clips']['Data']['4104776980463107687'].get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        
        with open(self.file_path_unzipped, 'rb') as file:
            for index, line in enumerate(file):
                if start_line <= index <= end_line:
                    relevant_lines.append(line.decode('utf-8'))
        
        start = False
        self.Level1['Clips']['Data']['4104776980463107687']['objects'] = {}
        data_dict = self.Level1['Clips']['Data']['4104776980463107687']['objects']
        current_item = None
        item_count = 0
        
        # Regex patterns to extract the Name and ID values
        name_pattern = re.compile(r'<Simple name="Name" value="([^"]+)"')
        id_pattern = re.compile(r'<Simple name="ID" value="([^"]+)"')
        
        for index, line in enumerate(relevant_lines):
            if not start:
                if self.Reconquest_sub_dicts['objects'] in line:
                    start = True
            else:
                if '<Item>' in line and (item_count == 0):
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
                            # Extract the Name and ID values within the Item
                            template_str = ''.join(data_dict[current_item]['template'])
                            name_match = name_pattern.search(template_str)
                            id_match = id_pattern.search(template_str)
                            if name_match:
                                name_value = name_match.group(1)
                                # Move the data to a new key based on name_value
                                data_dict[name_value] = data_dict.pop(current_item)
                                data_dict[name_value]['Name'] = name_value
                            if id_match:
                                id_value = id_match.group(1)
                                data_dict[name_value]['ID'] = id_value
                            current_item = None
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)
        
        # with open('ZXGame_Level4.json', 'w', encoding='utf-8') as json_file:
        #     json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

    def LevelFiveProcessing(self):
        # Retrieve the start and end lines for the specific ID
        start_line = self.Level1['Clips']['Data']['4104776980463107687'].get('StartLine')
        end_line = self.Level1['Clips']['Data']['4104776980463107687'].get('EndLine')
        
        if start_line is None or end_line is None:
            return
        
        relevant_lines = []
        
        with open(self.file_path_unzipped, 'rb') as file:
            for index, line in enumerate(file):
                if start_line <= index <= end_line:
                    relevant_lines.append(line.decode('utf-8'))
        
        start = False
        self.Level1['Clips']['Data']['4104776980463107687']['frames'] = {}
        data_dict = self.Level1['Clips']['Data']['4104776980463107687']['frames']
        current_item = None
        item_count = 0
        
        # Regex patterns to extract the Name and ID values
        id_pattern = re.compile(r'<Simple value="([^"]+)"')
        
        for index, line in enumerate(relevant_lines):
            if not start:
                if '<Dictionary name="ObjectInstances" keyType="System.UInt64, mscorlib" valueType="DXVision.DXProjectObjectInstance, DXVision">' in line:
                    start = True
            elif self.Reconquest_sub_dicts['objects'] in line:
                break
            else:
                if '<Item>' in line and (item_count == 0):
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
                            # Extract the Name and ID values within the Item
                            template_str = ''.join(data_dict[current_item]['template'])
                            id_match = id_pattern.search(template_str)
                            if id_match:
                                id_value = id_match.group(1)
                                data_dict[current_item]['ID'] = id_value
                            current_item = None
                            
                elif current_item is not None:
                    data_dict[current_item]['template'].append(line)

        new_data_dict = {}
        for key, value in data_dict.items():
            new_data_dict[data_dict[key]['ID']] = value
        
        self.Level1['Clips']['Data']['4104776980463107687']['frames'] = new_data_dict
        
        # Output the result to JSON for inspection

    def LevelSixProcessing(self):
        data_dict = self.Level1['Clips']['Data']['4104776980463107687']['frames']
        
        # Regex pattern to extract Simple name and value
        simple_pattern = re.compile(r'<Simple name="([^"]+)" value="([^"]+)"')

        for item in data_dict.keys():
            for line in data_dict[item]['template']:
                matches = simple_pattern.findall(line)
                if matches:
                    for name, value in matches:
                        data_dict[item][name] = value
        
        data_dict = self.Level1['Clips']['Data']['4104776980463107687']['objects']
        
        # Regex pattern to extract Simple name and value
        simple_pattern = re.compile(r'<Simple name="([^"]+)" value="([^"]+)"')

        for item in data_dict.keys():
            for line in data_dict[item]['template']:
                matches = simple_pattern.findall(line)
                if matches:
                    for name, value in matches:
                        data_dict[item][name] = value

    def print_json(self):
        with open('ZXGame.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.Level1, json_file, ensure_ascii=False, indent=4)