import os

def split_file(file_path, part_size=1 * 1024 * 1024, output_folder="output"):
    """
    Splits the file at the given file_path into smaller parts and saves them in the output_folder.
    
    :param file_path: Path to the input file to be split.
    :param part_size: Size of each part in bytes (default is 1 MB).
    :param output_folder: Folder where the parts will be saved (default is 'output').
    :return: List of paths to the part files created.
    """
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get the file name and extension
    base_name = os.path.basename(file_path)
    
    # Open the input file in binary mode
    with open(file_path, 'rb') as f:
        part_num = 1
        part_files = []
        while True:
            # Read part of the file
            chunk = f.read(part_size)
            if not chunk:
                break
            
            # Generate part file name
            part_file_name = f"{base_name}.part{part_num}"
            part_file_path = os.path.join(output_folder, part_file_name)
            
            # Write the chunk to a new part file
            with open(part_file_path, 'wb') as part_file:
                part_file.write(chunk)
            
            # Add the part file path to the list
            part_files.append(part_file_path)
            
            # Increment part number
            part_num += 1
    
    return part_files

# Example usage:
# file_path = "path/to/your/file.ext"
# split_file(file_path, part_size=1 * 1024 * 1024, output_folder="output_folder_path")

def combine_files(output_file_path, part_files, output_folder="output"):
    """
    Combines part files into a single output file.
    
    :param output_file_path: Path to the output file where parts will be combined.
    :param part_files: List of part file names (in correct order) to combine.
    :param output_folder: Folder where the parts are located (default is 'output').
    :return: Path to the combined output file.
    """
    # Open the output file in binary write mode
    with open(output_file_path, 'wb') as output_file:
        for part_file in part_files:
            part_file_path = os.path.join(output_folder, part_file)
            # Open each part file in binary read mode
            with open(part_file_path, 'rb') as part:
                # Read the content of each part and write it to the output file
                output_file.write(part.read())
    
    return output_file_path

#split_file("flutter_tutorial.pdf",1*1024*1024,"output")
combine_files("output/test1split.pdf",["flutter_tutorial.pdf.part1","flutter_tutorial.pdf.part2","flutter_tutorial.pdf.part3","flutter_tutorial.pdf.part4"],"output")

# Example usage:
# The list of part files should be in the correct order.
# part_files = ["file.ext.part1", "file.ext.part2", "file.ext.part3"]
# combined_file_path = "path/to/combined_file.ext"
# combine_files(combined_file_path, part_files, output_folder="output_folder_path")
