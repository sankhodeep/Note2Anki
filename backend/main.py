import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from .markdown_parser import parse_markdown
from .content_processor import reconstruct_markdown, chunk_content
from .ai.gemini import GeminiClient
from .ai.topic_selector import TopicSelector
from .ai.flashcard_generator import FlashcardGenerator
from .anki_connect import AnkiConnectClient

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "message": "Backend is running!"})

def initialize_clients(api_key: str, model_name: str):
    """Helper to initialize AI clients with the provided key and model."""
    gemini_client = GeminiClient(api_key=api_key, model_name=model_name)
    topic_selector = TopicSelector(gemini_client)
    flashcard_generator = FlashcardGenerator(gemini_client)
    return topic_selector, flashcard_generator

@app.route('/api/generate-topics', methods=['POST'])
def generate_topics_endpoint():
    data = request.json
    files_content = data.get('files', {})
    user_topics = data.get('user_topics', '')
    api_key = data.get('api_key', '')
    model_name = data.get('model_name', '')

    if not all([files_content, user_topics, api_key, model_name]):
        return jsonify({"error": "Missing required data: files, topics, API key, or model name."}), 400

    try:
        topic_selector, _ = initialize_clients(api_key, model_name)
        full_text = "\n\n".join(files_content.values())
        all_headings = parse_markdown(full_text)
        selected_topics = topic_selector.select_topics(all_headings, user_topics)
        return jsonify({"selected_topics": selected_topics, "all_headings": all_headings})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/api/refine-topics', methods=['POST'])
def refine_topics_endpoint():
    data = request.json
    all_headings = data.get('all_headings', [])
    user_topics = data.get('user_topics', '')
    selected_topics = data.get('selected_topics', [])
    api_key = data.get('api_key', '')
    model_name = data.get('model_name', '')

    if not all([all_headings, user_topics, selected_topics, api_key, model_name]):
        return jsonify({"error": "Missing required data for refinement."}), 400

    try:
        topic_selector, _ = initialize_clients(api_key, model_name)
        critique = topic_selector.critique_selection(all_headings, user_topics, selected_topics)
        if not critique:
            return jsonify({"error": "Failed to get a critique from the AI."}), 500
        refined_topics = topic_selector.refine_selection(all_headings, user_topics, critique)
        return jsonify({"refined_topics": refined_topics, "critique": critique})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/api/chunk-content', methods=['POST'])
def chunk_content_endpoint():
    data = request.json
    all_headings = data.get('all_headings', [])
    selected_topics = data.get('selected_topics', [])
    token_limit = data.get('token_limit', 5000)

    if not all([all_headings, selected_topics]):
        return jsonify({"error": "Missing headings or selected topics."}), 400

    try:
        reconstructed_md = reconstruct_markdown(all_headings, selected_topics)
        chunks = chunk_content(reconstructed_md, token_limit)
        return jsonify({"chunks": chunks, "reconstructed_content": reconstructed_md})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/api/generate-flashcards', methods=['POST'])
def generate_flashcards_endpoint():
    data = request.json
    chunks = data.get('chunks', [])
    api_key = data.get('api_key', '')
    model_name = data.get('model_name', '')
    anki_deck = data.get('anki_deck', '')
    anki_url = data.get('anki_connect_url', 'http://localhost:8765')

    if not all([chunks, api_key, model_name, anki_deck]):
        return jsonify({"error": "Missing required data for flashcard generation."}), 400

    try:
        _, flashcard_generator = initialize_clients(api_key, model_name)
        anki_client = AnkiConnectClient(anki_connect_url=anki_url)
        anki_client._invoke("deckNames")

        total_cards_added = 0
        for i, chunk in enumerate(chunks):
            sub_deck_name = f"{anki_deck}::Chunk_{i+1}"
            anki_client.create_deck(sub_deck_name)
            flashcards = flashcard_generator.generate_flashcards(chunk['content'])
            for card in flashcards:
                if anki_client.add_note(sub_deck_name, card['question'], card['answer']):
                    total_cards_added += 1

        return jsonify({"message": f"Success! Added {total_cards_added} flashcards to Anki.", "cards_added": total_cards_added})
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    print("Starting Flask server for AI Study Assistant...")
    app.run(host='0.0.0.0', port=5001, debug=False)