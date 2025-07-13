import os
from pathlib import Path


def get_files_info(working_directory, directory=None):
    if directory is None:
        return f'Error: "{directory}" is not a directory'

    full_path = os.path.join(working_directory, directory)

    if not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'

    working_directory = Path(working_directory).resolve()
    full_path = Path(full_path).resolve()

    if not full_path.is_relative_to(working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    content_of_directory = []

    for item in full_path.iterdir():
        item_info = f"{item.name}: file_size={item.stat().st_size} bytes, is_dir={'True' if item.is_dir() else 'False'}"
        content_of_directory.append(item_info)

    return "\n".join(content_of_directory)
