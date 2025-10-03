# AI Study Assistant

The AI Study Assistant is a powerful, locally-run application designed to supercharge your learning process. It intelligently analyzes your study materials, helps you select key topics, and automatically generates high-quality flashcards that can be directly imported into Anki, the popular spaced repetition software.

By leveraging the power of Google's Gemini models, this tool streamlines the creation of study aids, saving you time and helping you focus on what matters most.

## Features

-   **Intelligent Topic Selection**: Upload your markdown-based study notes, and the AI will suggest a list of relevant topics to focus on.
-   **AI-Powered Critique & Refinement**: Receive a detailed critique of the AI's own topic selection and allow it to self-correct for the best possible results.
-   **Automatic Flashcard Generation**: Transforms your selected content into concise, effective question-and-answer flashcards.
-   **Direct Anki Integration**: Automatically creates new sub-decks in your Anki collection and populates them with the generated flashcards.
-   **Customizable Content Chunking**: Splits large documents into manageable chunks to respect AI model token limits, ensuring no content is left behind.
-   **Flexible Model Selection**: Choose between different Gemini models (e.g., Gemini 1.5 Flash, Gemini 1.5 Pro) to balance speed and power.

## How It Works

The application consists of a Python Flask backend that serves a simple HTML/JavaScript frontend.

1.  **Content Upload**: The user selects one or more markdown files from their local machine.
2.  **Topic Proposal**: The backend parses the markdown to identify all headings. It sends this structure, along with the user's study goals, to the Gemini API, which returns a list of suggested topics.
3.  **Refinement Loop (Optional)**: The user can trigger a "critique" step, where the AI evaluates its own suggestions and refines the topic list based on its own feedback.
4.  **Content Chunking**: Based on the final topic selection, the relevant markdown content is reconstructed and split into smaller chunks that fit within the selected Gemini model's token limit.
5.  **Flashcard Generation**: Each chunk is sent to the Gemini API to generate a set of flashcards.
6.  **Anki Export**: The generated flashcards are sent to the user's local Anki desktop application via the AnkiConnect add-on.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

-   **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
-   **Anki**: [Download Anki](https://apps.ankiweb.net/)
-   **AnkiConnect Add-on**:
    -   Open Anki -> Tools -> Add-ons.
    -   Click "Get Add-ons..." and enter the code: `2055492159`
    -   Restart Anki.
-   **Google Gemini API Key**:
    -   Go to [Google AI Studio](https://aistudio.google.com/).
    -   Click "Get API Key" and create a new key.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ai-study-assistant.git
    cd ai-study-assistant
    ```

2.  **Install backend dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

## Configuration

The application needs your Google Gemini API key to function. You can provide this key in two ways:

1.  **Environment Variable (Recommended)**: Set an environment variable named `GEMINI_API_KEY`.
    -   **macOS/Linux**: `export GEMINI_API_KEY='your_api_key_here'`
    -   **Windows**: `set GEMINI_API_KEY='your_api_key_here'`

2.  **Through the UI**: If the environment variable is not set, you can paste your API key directly into the input field in the web interface.

## Running the Application

1.  **Start the backend server:**
    ```bash
    python -m backend.main
    ```
    The server will start on `http://localhost:5001`.

2.  **Access the frontend:**
    -   Open your web browser and navigate to [http://localhost:5001](http://localhost:5001).

## Usage

1.  **Select Model & API Key**: Choose a Gemini model from the dropdown. If you haven't set the environment variable, paste your API key.
2.  **Upload Notes**: Click "Choose Files" and select one or more `.md` files containing your study notes.
3.  **Define Topics**: In the "Study Topics" text area, describe what you want to learn (e.g., "the main concepts of machine learning").
4.  **Generate Topics**: Click "Generate Topics". The AI will analyze your files and propose a list of topics, which will appear in the "Selected Topics" area.
5.  **Refine (Optional)**: Click "Refine Topics" to have the AI critique and improve its own selection.
6.  **Generate Flashcards**: Enter your desired main Anki deck name and click "Generate & Add to Anki".
7.  **Check Anki**: The application will create sub-decks within your specified main deck (e.g., `MyDeck::Chunk_1`) and populate them with flashcards. Open Anki to see your new cards!