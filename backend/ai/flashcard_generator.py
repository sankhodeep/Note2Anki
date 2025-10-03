import json
from typing import List, Dict

from .gemini import GeminiClient

class FlashcardGenerator:
    """
    Uses an AI model to generate flashcards from a chunk of text.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initializes the FlashcardGenerator.

        Args:
            gemini_client: An instance of the GeminiClient for API communication.
        """
        self.client = gemini_client

    def _create_flashcard_prompt(self, content_chunk: str) -> str:
        """Creates the prompt for the AI to generate flashcards."""
        return f"""
You are a helpful study assistant. Your task is to create a set of flashcards from the provided text content.

**Instructions:**
1.  Read the "Text Content" below.
2.  Identify the key concepts, definitions, and important facts.
3.  Generate a list of question-and-answer pairs based on this information.
4.  Return the flashcards as a JSON array of objects, where each object has a "question" key and an "answer" key.
5.  Ensure the questions are clear and the answers are concise and accurate.

**Text Content:**
---
{content_chunk}
---

**Your Output (JSON array of objects):**
"""

    def _parse_json_response(self, response_text: str) -> List[Dict[str, str]]:
        """Safely parses JSON from the AI's response."""
        try:
            cleaned_response = response_text.strip().replace('```json', '').replace('```', '').strip()
            flashcards = json.loads(cleaned_response)
            if isinstance(flashcards, list) and all(isinstance(fc, dict) and 'question' in fc and 'answer' in fc for fc in flashcards):
                return flashcards
            return []
        except (json.JSONDecodeError, TypeError):
            print(f"DEBUG: Failed to parse JSON response for flashcards: {response_text}")
            return []

    def generate_flashcards(self, content_chunk: str) -> List[Dict[str, str]]:
        """
        Generates flashcards for a given chunk of content.

        Args:
            content_chunk: A string containing the text to generate flashcards from.

        Returns:
            A list of flashcard dictionaries (e.g., [{'question': '...', 'answer': '...'}]).
        """
        prompt = self._create_flashcard_prompt(content_chunk)
        response_text = self.client.generate_content(prompt)
        return self._parse_json_response(response_text)

# if __name__ == '__main__':
#     print("Running FlashcardGenerator test...")
#     try:
#         # This test requires a valid GEMINI_API_KEY in the.
#         gemini_client = GeminiClient()
#         generator = FlashcardGenerator(gemini_client)

#         sample_content = """
# # The Sun
# The Sun is the star at the center of the Solar System. It is a nearly perfect ball of hot plasma, heated to incandescence by nuclear fusion reactions in its core. The Sun's diameter is about 1.39 million kilometers, or 109 times that of Earth. Its mass is about 330,000 times that of Earth.
#         """

#         print(f"\nGenerating flashcards for sample content...")
#         flashcards = generator.generate_flashcards(sample_content)

#         print(f"Generated {len(flashcards)} flashcards:")
#         for fc in flashcards:
#             print(f"  Q: {fc['question']}")
#             print(f"  A: {fc['answer']}")

#         assert isinstance(flashcards, list)
#         assert len(flashcards) > 0
#         assert 'question' in flashcards[0]
#         assert 'answer' in flashcards[0]

#         print("\nFlashcardGenerator test passed!")

#     except Exception as e:
#         print(f"An unexpected error occurred during the test: {e}")