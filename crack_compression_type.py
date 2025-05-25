import subprocess
import os
from pathlib import Path

def compress_files_with_levels_and_word_size(sevenzip_executable, input_file, output_folder, password):
    global original_size
    # Ensure the output folder exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    compression_levels = range(10)  # Compression levels from 0 to 9
    word_sizes = ['8', '16', '24', '32', '64','128','192','256','258']  # Example word sizes in bits
    archive_types = ['-tzip','7z','gzip','rar','iso','lzma']
    
    for archive_type in archive_types:
        for level in compression_levels:
            for word_size in word_sizes:
                # Create a subfolder for each combination
                subfolder = Path(f'{output_folder}_{archive_type}_level{level}_word{word_size}')
                subfolder.mkdir(parents=True, exist_ok=True)
                output_file = subfolder / f"{input_file.stem}.TABProject"
                command = [
                    sevenzip_executable,
                    'a',  # Add to archive
                    str(output_file),  # The output archive file
                    str(input_file),  # The input file to compress
                    archive_type,  # Archive type
                    f'-mx={level}',  # Compression level
                    f'-mfb={word_size}',  # Word size
                    f'-p{password}',  # Password for the archive
                ]

                try:
                    # Run the command and capture the output
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    #print(f"Created archive: {output_file}")
                except subprocess.CalledProcessError as e:
                    pass
                    #print(f"Failed to create archive {output_file}: {e}")
                compressed_size = output_file.stat().st_size
                print(f"{compressed_size}")
                if original_size == compressed_size:
                    print("FUCK YES")
                
            
            
# Example usage
sevenzip_executable = r'C:/Program Files/7-Zip/7z.exe'
input_file = Path(r'C:\Users\Josh\Desktop\temp_testing\New Level1')
input_file1 = Path(r'C:\Users\Josh\Desktop\temp_testing\New Level1.TABProject')
output_folder = r'C:\Users\Josh\Desktop\temp_testing\compressed'
password = '5132121111451334062066133244'

global original_size
original_size = input_file1.stat().st_size

compress_files_with_levels_and_word_size(sevenzip_executable, input_file, output_folder, password)




print(f"Original file size: {original_size} bytes")