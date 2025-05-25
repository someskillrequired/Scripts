import subprocess

password_list = ["5132121111451334062066133244"]

password_list = list(set(password_list))

def unzip_file_with_7zip(input, output, password_list):
    sevenzip_executable = r'C:\Program Files\7-Zip\7z.exe'  # Adjust the path based on your installation
    for password in password_list:
        try:
            command = [
                sevenzip_executable,
                'x',  # Extract files with full paths
                '-y',  # Assume Yes on all queries (overwrite files without prompting)
                f'-p{password}',  # Password for the archive
                f'-o{output}',  # Output directory
                input  # The path of the archive to extract
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Successfully extracted with password: {password}")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to extract with password: {password}. Trying next...")

    print("All passwords attempted. Unable to extract the file.")
    return False

# Example usage
file_path = 'D:/SteamLibrary/steamapps/common/They Are Billions/SniperEdition.dat'
output_path = 'D:/SteamLibrary/steamapps/common/They Are Billions/ZXGame_Data/Images/Campaign/'
unzip_file_with_7zip(file_path, output_path,password_list)

