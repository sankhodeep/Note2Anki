import json
from typing import List, Dict, Any

from .gemini import GeminiClient

class TopicSelector:
    """
    Uses an AI model to select, critique, and refine relevant topics
    from a list of markdown headings.
    """

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    def _create_selection_prompt(self, all_headings: List[Dict[str, Any]], user_topics: str) -> str:
        heading_titles = [f"{'#' * h['level']} {h['title']}" for h in all_headings]
        return f"""
You are an intelligent study assistant. Your task is to select relevant headings from a list, based on a user's stated topics of interest.

**Instructions:**
1. Analyze the "List of Important Topics" from the user.
2. Review the "List of All Headings" from the notes.
3. Return a JSON array of strings containing the exact titles of the headings that are relevant.
4. **Crucially**: Only include a main heading if ALL of its subheadings are relevant. If only some subheadings are relevant, list the specific subheadings instead.
5. Do not invent new headings. Only return headings that exist in the provided list.

**List of Important Topics:**
{user_topics}

**List of All Headings:**
```json
{json.dumps(heading_titles, indent=2)}
```

**Your Output (JSON array of strings):**
"""

    def _create_critique_prompt(self, all_headings: List[Dict[str, Any]], user_topics: str, selected_topics: List[str]) -> str:
        heading_titles = [f"{'#' * h['level']} {h['title']}" for h in all_headings]
        return f"""
You are a meticulous and critical AI evaluator. Your task is to assess a topic selection made by another AI.

**Context:**
- A user specified their "Important Topics".
- An AI assistant reviewed a "List of All Headings" from the user's notes.
- The assistant produced a "Selected Topics" list.

**Your Task:**
Evaluate how well the "Selected Topics" list matches the user's "Important Topics". Provide a detailed report in JSON format with the following structure:
- `reliability_score`: A number between 0 and 100 representing your confidence in the selection's accuracy.
- `wrongly_included`: A list of topics from "Selected Topics" that you believe are irrelevant.
- `should_be_included`: A list of topics from "All Headings" that were missed but are relevant.
- `explanation`: A detailed paragraph explaining your reasoning for the score and suggested changes.

**User's Important Topics:**
{user_topics}

**List of All Headings:**
```json
{json.dumps(heading_titles, indent=2)}
```

**AI's Selected Topics:**
```json
{json.dumps(selected_topics, indent=2)}
```

**Your Output (JSON object):**
"""

    def _create_refinement_prompt(self, all_headings: List[Dict[str, Any]], user_topics: str, critique_report: Dict[str, Any]) -> str:
        heading_titles = [f"{'#' * h['level']} {h['title']}" for h in all_headings]
        return f"""
You are an intelligent study assistant. Your previous attempt at selecting topics was reviewed by a critic. Now, you must generate a new, corrected list of topics based on the critic's feedback.

**Original Goal:** Select relevant headings based on the user's "Important Topics".

**Critic's Report:**
```json
{json.dumps(critique_report, indent=2)}
```

**Your Task:**
Generate a new, final list of topics.
- **Incorporate the critic's feedback**: Add the topics the critic said `should_be_included` and remove the ones identified as `wrongly_included`.
- Refer back to the "List of All Headings" to ensure the titles are exact.
- Return your final, corrected list as a JSON array of strings.

**User's Important Topics:**
{user_topics}

**List of All Headings:**
```json
{json.dumps(heading_titles, indent=2)}
```

**Your New, Corrected Output (JSON array of strings):**
"""

    def _parse_json_response(self, response_text: str):
        """Safely parses JSON from the AI's response, cleaning it first."""
        try:
            # Clean potential markdown code blocks and trailing commas
            cleaned_response = response_text.strip().replace('```json', '').replace('```', '').strip()
            # Handle potential trailing commas in JSON objects/arrays
            cleaned_response = cleaned_response.rstrip(',')
            if cleaned_response.endswith(']'):
                pass # Looks okay
            elif cleaned_response.endswith('}'):
                pass # Looks okay

            return json.loads(cleaned_response)
        except (json.JSONDecodeError, TypeError):
            print(f"DEBUG: Failed to parse JSON response: {response_text}")
            return None

    def select_topics(self, all_headings: List[Dict[str, Any]], user_topics: str) -> List[str]:
        prompt = self._create_selection_prompt(all_headings, user_topics)
        response_text = self.client.generate_content(prompt)
        parsed_response = self._parse_json_response(response_text)
        return parsed_response if isinstance(parsed_response, list) else []

    def critique_selection(self, all_headings: List[Dict[str, Any]], user_topics: str, selected_topics: List[str]) -> Dict[str, Any]:
        prompt = self._create_critique_prompt(all_headings, user_topics, selected_topics)
        response_text = self.client.generate_content(prompt)
        parsed_response = self._parse_json_response(response_text)
        return parsed_response if isinstance(parsed_response, dict) else {}

    def refine_selection(self, all_headings: List[Dict[str, Any]], user_topics: str, critique_report: Dict[str, Any]) -> List[str]:
        prompt = self._create_refinement_prompt(all_headings, user_topics, critique_report)
        response_text = self.client.generate_content(prompt)
        parsed_response = self._parse_json_response(response_text)
        return parsed_response if isinstance(parsed_response, list) else []


# if __name__ == '__main__':
#     print("Running TopicSelector full workflow test...")
#     try:
#         gemini_client = GeminiClient()
#         selector = TopicSelector(gemini_client)

#         # Sample data
#         sample_headings = [
#             {'level': 1, 'title': 'The Solar System', 'content': '...'},
#             {'level': 2, 'title': 'Inner Planets', 'content': '...'},
#             {'level': 3, 'title': 'Earth', 'content': '...'},
#             {'level': 3, 'title': 'Mars', 'content': '...'},
#             {'level': 2, 'title': 'Outer Planets', 'content': '...'},
#             {'level': 3, 'title': 'Jupiter', 'content': '...'},
#             {'level': 3, 'title': 'Saturn', 'content': '...'},
#             {'level': 1, 'title': 'Stellar Evolution', 'content': '...'},
#             {'level': 2, 'title': 'Nebulae', 'content': '...'}
#         ]
#         user_input_topics = "I need to study the planets, but not Earth. Also interested in nebulae."

#         # 1. Initial Selection
#         print("\n--- Step 1: Initial Topic Selection ---")
#         initial_selection = selector.select_topics(sample_headings, user_input_topics)
#         print(f"Initial AI selection: {initial_selection}")
#         assert isinstance(initial_selection, list)

#         # 2. Critique
#         print("\n--- Step 2: Critique of the Selection ---")
#         # Let's pretend the initial selection was imperfect for testing purposes
#         # A plausible mistake would be including "Inner Planets" instead of just "Mars"
#         test_selection = ["## Inner Planets", "## Outer Planets", "## Nebulae"]
#         print(f"Running critique on a test selection: {test_selection}")
#         critique = selector.critique_selection(sample_headings, user_input_topics, test_selection)
#         print(f"Critique Report: {json.dumps(critique, indent=2)}")
#         assert isinstance(critique, dict)
#         assert 'reliability_score' in critique
#         assert 'explanation' in critique

#         # 3. Refinement
#         print("\n--- Step 3: Refine Selection based on Critique ---")
#         # A good critique should suggest removing "## Inner Planets" and adding "### Mars"
#         # and keeping "## Nebulae"
#         refined_selection = selector.refine_selection(sample_headings, user_input_topics, critique)
#         print(f"Refined AI selection: {refined_selection}")
#         assert isinstance(refined_selection, list)
#         assert "### Mars" in refined_selection
#         assert "## Nebulae" in refined_selection
#         # The AI should be smart enough not to include the parent heading if the user said "not Earth"
#         assert "## Inner Planets" not in refined_selection

#         print("\nTopicSelector full workflow test passed!")

#     except Exception as e:
#         print(f"An unexpected error occurred during the test: {e}")