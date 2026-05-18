from functions.get_files_info import get_files_info  # adjust import path as needed


def format_output(directory, result):
    if directory == ".":
        directory = "current"

    formatted_result = f"Result for {directory}  directory:\n"
    for result_line in result.splitlines():
        if result.startswith("Error:"):
            formatted_result += f"    {result_line}\n"
        else:
            formatted_result += f"  - {result_line}\n"
    return formatted_result


directories = [".", "pkg", "/bin", "../"]
for directory in directories:
    result = get_files_info("calculator", directory)
    print(format_output(directory, result))
