# Sales Call Insights Generator

This project allows you to generate insights from a sales call audio file using AI-powered transcription and analysis. The script utilizes **AssemblyAI** for audio transcription and **Anthropic** for analyzing the call and providing insights such as summaries, key discussion points, customer objections, and recommended actions.

## Requirements

- **Python 3.x**
- **AssemblyAI API Key**: For audio transcription.
- **Anthropic API Key**: For generating insights from the call transcript.

## Installation

1. **Clone the repository** (if you’re using Git):

    ```bash
    git clone https://github.com/CosmicMagnetar/Insights-Generator.git
    cd Insights-Generator
    ```

2. **Install required Python packages** using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

   Where `requirements.txt` should contain:

    ```
    assemblyai
    fpdf
    anthropic
    ```

   You can also manually install the dependencies using:

    ```bash
    pip install assemblyai fpdf anthropic
    ```

## Configuration

Before running the script, ensure that you have the necessary API keys:

1. **AssemblyAI API Key**: You need to sign up at [AssemblyAI](https://www.assemblyai.com/) and obtain your API key.
2. **Anthropic API Key**: You need to sign up at [Anthropic](https://www.anthropic.com/) and obtain your API key.

You can set the API keys directly in the script, or use environment variables:

- `ASSEMBLYAI_API_KEY`: Set this variable to your AssemblyAI API key.
- `ANTHROPIC_API_KEY`: Set this variable to your Anthropic API key.

Alternatively, you can pass the API keys directly in the command line when running the script.

## Running the Script

### Command-Line Usage

To run the script, execute the following command in your terminal:

```bash
python main.py <audio_file_path> --assemblyai_api_key <ASSEMBLYAI_API_KEY> --anthropic_api_key <ANTHROPIC_API_KEY>
