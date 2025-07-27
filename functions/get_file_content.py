import os
import sys
from pathlib import Path

from google.genai import types

# Add the parent directory to Python path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MAX_FILE_READ_BYTES

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file content in the specified directory, constrained to the working directory, if file size more than 10000 bytes, file will be truncated with a message in the end of the file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="file name to load content from, inside the working directory. file_path is mandatory. If not provided, cause an error.",
            ),
        },
    ),
)


def get_file_content(working_directory, file_path):
    full_path = os.path.join(working_directory, file_path)

    if not os.path.isfile(full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    working_directory = Path(working_directory).resolve()
    full_path = Path(full_path).resolve()

    if not full_path.is_relative_to(working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    try:
        file_size = full_path.stat().st_size
        with open(full_path, "r", encoding="utf-8") as file:
            content = file.read(
                MAX_FILE_READ_BYTES
            )  # Read up to MAX_FILE_READ_BYTES characters
        if file_size > MAX_FILE_READ_BYTES:
            content += f'\n[...File "{full_path}" truncated at {MAX_FILE_READ_BYTES} characters]'
        return content
    except Exception as e:
        return f'Error: reading file "{file_path}": {e}'
