import json
import requests
from typing import List, Dict, Optional

class AnkiConnectClient:
    """
    A client for interacting with the AnkiConnect add-on for Anki.
    Allows for programmatic creation of decks and addition of notes.
    """

    def __init__(self, anki_connect_url: str = "http://localhost:8765"):
        """
        Initializes the AnkiConnect client.

        Args:
            anki_connect_url: The URL of the AnkiConnect server.
        """
        self.url = anki_connect_url
        self.session = requests.Session()

    def _invoke(self, action: str, **params) -> Dict:
        """
        Invokes a specific action on the AnkiConnect API.

        Args:
            action: The name of the AnkiConnect action to perform.
            params: The parameters for the action.

        Returns:
            The JSON response from the API as a dictionary.

        Raises:
            ConnectionError: If the client cannot connect to the AnkiConnect server.
            Exception: For other API-level errors.
        """
        payload = {"action": action, "version": 6, "params": params}
        try:
            response = self.session.post(self.url, data=json.dumps(payload))
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            response_json = response.json()
            if response_json.get("error"):
                raise Exception(f"AnkiConnect API error: {response_json['error']}")
            return response_json
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to AnkiConnect at {self.url}. Is Anki running with AnkiConnect installed?") from e

    def deck_exists(self, deck_name: str) -> bool:
        """Checks if a deck with the given name already exists."""
        response = self._invoke("deckNames")
        return deck_name in response.get("result", [])

    def create_deck(self, deck_name: str) -> Optional[int]:
        """
        Creates a new deck in Anki. Handles nested decks (e.g., "Parent::Child").

        Args:
            deck_name: The name of the deck to create.

        Returns:
            The deck ID if created successfully, otherwise None.
        """
        if self.deck_exists(deck_name):
            print(f"Deck '{deck_name}' already exists.")
            return None

        response = self._invoke("createDeck", deck=deck_name)
        return response.get("result")

    def add_note(self, deck_name: str, question: str, answer: str) -> Optional[int]:
        """
        Adds a new basic note (flashcard) to a specified deck.

        Args:
            deck_name: The name of the deck to add the note to.
            question: The text for the 'Front' of the card.
            answer: The text for the 'Back' of the card.

        Returns:
            The note ID if created successfully, otherwise None.
        """
        note_params = {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": question,
                    "Back": answer
                },
                "tags": ["auto-generated"]
            }
        }
        response = self._invoke("addNote", **note_params)
        return response.get("result")

# if __name__ == '__main__':
#     print("Running AnkiConnectClient demonstration...")
#     print("This script demonstrates how to use the client. It is not a self-running test.")
#     print("To use this, you MUST have Anki running with the AnkiConnect add-on installed.")

#     try:
#         # 1. Initialize the client
#         anki_client = AnkiConnectClient()
#         print("\nAttempting to connect to AnkiConnect...")

#         # 2. Check connection by getting deck names (a safe, read-only action)
#         deck_names = anki_client._invoke("deckNames").get("result")
#         print(f"Successfully connected! Found {len(deck_names)} decks.")

#         # 3. Define a new deck and some sample notes
#         main_deck = "MyStudyNotes"
#         sub_deck = f"{main_deck}::GeneratedFlashcards_Demo"
#         sample_flashcards = [
#             {"question": "What is AnkiConnect?", "answer": "An Anki add-on that exposes a local API."},
#             {"question": "What format does the API use?", "answer": "JSON."}
#         ]

#         # 4. Create the deck
#         print(f"\nAttempting to create deck: '{sub_deck}'")
#         deck_id = anki_client.create_deck(sub_deck)
#         if deck_id:
#             print(f"Deck created successfully with ID: {deck_id}")
#         else:
#             print("Deck creation skipped or failed.")

#         # 5. Add the notes
#         print(f"\nAdding {len(sample_flashcards)} notes to '{sub_deck}'...")
#         for card in sample_flashcards:
#             note_id = anki_client.add_note(sub_deck, card["question"], card["answer"])
#             if note_id:
#                 print(f"  - Added note with ID: {note_id}")
#             else:
#                 print(f"  - Failed to add note: {card['question']}")

#         print("\nAnkiConnectClient demonstration finished.")

#     except ConnectionError as e:
#         print(f"\nDEMO FAILED: {e}")
#         print("Please ensure Anki is running and the AnkiConnect add-on is installed and configured.")
#     except Exception as e:
#         print(f"\nAn unexpected error occurred during the demo: {e}")