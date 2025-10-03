import os
from google import genai
from google.genai import types
from typing import Optional

class GeminiClient:
    """
    A client for interacting with the Google Gemini API using the new
    genai.Client interface suitable for Gemini 2.5 models.
    """
    def __init__(self, api_key: Optional[str], model_name: str):
        """
        Initializes the Gemini client.

        Args:
            api_key: The Google AI API key. Falls back to GEMINI_API_KEY env var.
            model_name: The model to use (e.g., "gemini-2.5-pro").

        Raises:
            ValueError: If the API key is not provided.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Please provide it as an argument "
                "or set the GEMINI_API_KEY environment variable."
            )

        # The new client does not require the 'models/' prefix.
        self.model_name = model_name.replace("models/", "")
        self.client = genai.Client(api_key=self.api_key)

    def generate_content(self, prompt: str) -> str:
        """
        Generates content by calling the streaming API and aggregating the response.

        Args:
            prompt: The prompt to send to the AI model.

        Returns:
            The aggregated text from the model's response or an error string.
        """
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]

        # This configuration is based on the user-provided snippet for 2.5 models.
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
            ),
        )

        try:
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            )

            full_response = "".join(chunk.text for chunk in response_stream if hasattr(chunk, 'text'))

            if full_response:
                return full_response
            else:
                # The new API may not provide feedback in the same way.
                # A generic error is returned if the response is empty.
                return "Error: The response was empty. It may have been blocked for safety reasons."

        except Exception as e:
            return f"An error occurred during API call: {type(e).__name__} - {e}"

# Note: The original __main__ block is removed as it was based on the old API
# and would require significant changes to test the new streaming-based client
# in a simple script. The functionality will be tested through the application's endpoints.