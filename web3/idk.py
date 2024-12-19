import requests

def send_prompt_to_lmstudio(prompt, api_url="http://localhost:1234/api/completions"):
    # Set up the payload with the prompt and additional parameters
    payload = {
        "prompt": prompt,
        "max_new_tokens": 100,  # Adjust as needed for your use case
        "temperature": 0.7,     # Sampling temperature for randomness
        "top_p": 0.9,          # Nucleus sampling probability
        "stop": ["\n"]       # Define stop tokens
    }

    try:
        # Send the request to the LM Studio API
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an error if the request fails

        # Parse and return the AI's response
        ai_response = response.json()
        return ai_response.get("text", "No response text found.")

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    import sys

    # Check for input and output file arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        # Read the prompt from the input file
        with open(input_file, "r") as f:
            user_prompt = f.read().strip()

        # Send the prompt and get the response
        response_text = send_prompt_to_lmstudio(user_prompt)

        # Write the AI's response to the output file
        with open(output_file, "w") as f:
            f.write(response_text)

        print(f"Response written to {output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
