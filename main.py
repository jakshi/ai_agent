import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types


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
    try:
        # Generate content using the provided prompt
        response = client.models.generate_content(
            model=args.model,
            contents=messages,
        )

        print(response.text)

        if args.verbose:
            print(f"User prompt: {prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    except Exception as e:
        print(f"Error generating content: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
