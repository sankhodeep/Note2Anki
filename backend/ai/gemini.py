import os
import google.generativeai as genai
from typing import Optional

class GeminiClient:
    """
    A client for interacting with the Google Gemini API.

    This client handles API key configuration and provides a method to
    generate content from a given prompt.
    """
    def __init__(self, api_key: Optional[str], model_name: str):
        """
        Initializes the Gemini client.

        The API key is configured from the `api_key` argument, or falls back to
        the `GEMINI_API_KEY` environment variable.

        Args:
            api_key: The Google AI API key.
            model_name: The specific Gemini model to use (e.g., "gemini-2.5-pro").

        Raises:
            ValueError: If the API key or model name is not provided, or if the
                        API key is not found in the environment variables.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Please provide it as an argument "
                "or set the GEMINI_API_KEY environment variable."
            )

        # The model name needs the 'models/' prefix for the API
        prefixed_model_name = f"models/{model_name}" if not model_name.startswith("models/") else model_name

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(prefixed_model_name)

    def generate_content(self, prompt: str) -> str:
        """
        Generates content using the configured Gemini model.

        Args:
            prompt: The prompt to send to the AI model.

        Returns:
            The text part of the generated content or an error string.
        """
        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text'):
                return response.text
            else:
                # If the response was blocked, provide that feedback.
                return f"Error: The response was blocked or empty. Feedback: {response.prompt_feedback}"
        except Exception as e:
            return f"An error occurred during API call: {type(e).__name__} - {e}"

# if __name__ == '__main__':
#     # This is a simple test block to verify the client works.
#     # It requires a valid GEMINI_API_KEY in the environment to run.
#     print("Running GeminiClient test with model 'models/gemini-pro-latest'...")
#     try:
#         api_key_env = os.getenv("GEMINI_API_KEY")
#         if not api_key_env:
#             raise ValueError("GEMINI_API_KEY environment variable not found.")

#         client = GeminiClient(api_key=api_key_env)
#         test_prompt = "Explain the concept of 'hello world' in programming in one sentence."
#         response = client.generate_content(test_prompt)

#         print(f"DEBUG: Full response from generate_content:\n---\n{response}\n---")

#         # More robust assertion: Check if the response is not an error and has content.
#         assert not response.startswith("An error occurred")
#         assert not response.startswith("Error:")
#         assert len(response) > 10 # Check for a reasonably non-empty response

#         print("Test prompt response:")
#         print(response)
#         print("\nGeminiClient test passed!")

#     except (ValueError, AssertionError) as e:
#         print(f"Test failed: {e}")
#         print("Please ensure your GEMINI_API_KEY is valid and set in your environment.")
#     except Exception as e:
#         print(f"An unexpected error occurred during the test: {type(e).__name__} - {e}")