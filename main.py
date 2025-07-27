import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import SYSTEM_PROMPT
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import schema_write_file, write_file


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    functions = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    function_name = function_call_part.name

    function = functions.get(function_name)

    if not function:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        function_result = function(
            working_directory="./calculator",
            **function_call_part.args,
        )
        if verbose:
            print(f"Function result: {function_result}")
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    except Exception as e:
        error_message = f"Error calling function {function_name}: {str(e)}"
        if verbose:
            print(error_message)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": error_message},
                )
            ],
        )


def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Generate content using Gemini AI")
    parser.add_argument("prompt", help="The prompt to send to the AI model")
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash",
        help="Model to use (default: gemini-2.0-flash)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about the request and response",
    )

    args = parser.parse_args()

    # Load environment and initialize client
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=api_key)

    prompt = args.prompt

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    try:
        i = 0
        while i <= 20:
            i += 1
            # Generate content using the provided prompt
            response = client.models.generate_content(
                model=args.model,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=SYSTEM_PROMPT
                ),
            )

            for candidate in response.candidates:
                messages.append(candidate.content)

            if response.function_calls:
                for function_call in response.function_calls:
                    try:
                        function_call_result = (
                            call_function(function_call, verbose=args.verbose)
                            .parts[0]
                            .function_response.response
                        )

                        messages.append(
                            types.Content(
                                role="tool",
                                parts=[
                                    types.Part.from_function_response(
                                        name=function_call.name,
                                        response=function_call_result,
                                    )
                                ],
                            )
                        )
                        if args.verbose:
                            print(f"-> {function_call_result}")
                    except Exception as e:
                        print(f"Error calling function {function_call.name}: {e}")
                        exit(1)
                continue  # Skip to the next iteration if function calls are present

            if args.verbose:
                print(f"User prompt: {prompt}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(
                    f"Response tokens: {response.usage_metadata.candidates_token_count}"
                )

            if response.text:
                print(response.text)
                break  # Exit loop if text response is received

    except Exception as e:
        print(f"Error generating content: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
