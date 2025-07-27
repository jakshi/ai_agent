import os
import subprocess
from pathlib import Path

from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file in the specified working directory, constrained to the working directory. Accepts a file path and optional arguments to pass to the script. If the file does not exist, is not a Python file, or is outside the working directory, an error will be returned.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory. If not provided, cause an error. if file suffix is not .py, cause an error.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to the Python script. If not provided, no arguments will be passed.",
                ),
                description="List of arguments to pass to the Python script.",
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=[]):
    try:
        # Resolve paths first (before existence check)
        working_directory = Path(working_directory).resolve()
        full_path = (Path(working_directory) / file_path).resolve()

        if not full_path.is_relative_to(working_directory):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not full_path.exists():
            return f'Error: File "{file_path}" not found.'
        if full_path.suffix != ".py":
            return f'Error: "{file_path}" is not a Python file.'

        # Build command
        command = ["python", str(full_path)]

        # Add args if provided
        if args:
            if isinstance(args, list):
                command.extend(args)
            else:
                # If args is a single string, convert to list
                command.append(str(args))

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(working_directory),
        )

        output = ""
        if result.stdout:
            output += f"STDOUT: {result.stdout}\n"
        if result.stderr:
            output += f"STDERR: {result.stderr}\n"
        if not output:
            output = "No output produced."
        if result.returncode != 0:
            output += f"Process exited with code {result.returncode}.\n"
        return output

    except Exception as e:
        return f"Error: executing Python file: {e}"
