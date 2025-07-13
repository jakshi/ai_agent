import os
import subprocess
from pathlib import Path


def run_python_file(working_directory, file_path):
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
