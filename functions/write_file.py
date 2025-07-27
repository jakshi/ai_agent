import os
from pathlib import Path

from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write content to a file in the specified working directory, constrained to the working directory. If the file does not exist, it will be created. If the file is outside the working directory, an error will be returned.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory. If not provided, cause an error.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file. If not provided, cause an error.",
            ),
        },
    ),
)


def write_file(working_directory, file_path, content):
    try:
        # Resolve paths first (before existence check)
        working_directory = Path(working_directory).resolve()
        full_path = (Path(working_directory) / file_path).resolve()

        if not full_path.is_relative_to(working_directory):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        full_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # Ensure parent directories exist

        full_path.touch(exist_ok=True)  # Create the file if it doesn't exist

        with open(full_path, "w", encoding="utf-8") as file:
            file.write(content)

        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except Exception as e:
        return f'Error: creating file "{file_path}" in "{working_directory}: {e}'
