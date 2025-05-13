import argparse
import os
import assemblyai as aai
from fpdf import FPDF
import requests
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Generate insights from a sales call audio file.")
    parser.add_argument('audio_file', type=str, help="Path to the audio file (e.g., 'audio/sales-call.mp3')")
    parser.add_argument('--assemblyai_api_key', type=str, help="AssemblyAI API Key")
    parser.add_argument('--openrouter_api_key', type=str, help="OpenRouter API Key")
    return parser.parse_args()

args = parse_args()

aai.settings.api_key = args.assemblyai_api_key or os.getenv("ASSEMBLYAI_API_KEY")
OPENROUTER_API_KEY = args.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")

if not aai.settings.api_key or not OPENROUTER_API_KEY:
    raise RuntimeError("Both AssemblyAI and OpenRouter API keys are required.")

audio_url = args.audio_file

config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
transcript = aai.Transcriber(config=config).transcribe(audio_url)

if transcript.status == "error":
    raise RuntimeError(f"Transcription failed: {transcript.error}")

transcript_text = transcript.text

def clean_text(text):
    text = re.sub(r'[\*"]', '', text).strip()
    text = text.replace("•", "-")
    return text

def generate_insight(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API Error {response.status_code}: {response.text}")

    return clean_text(response.json()['choices'][0]['message']['content'])

summary_prompt = f"""
You are a professional sales analyst. Provide a bullet-point summary of the call covering:

- Purpose of the call
- Customer concerns
- Product features discussed
- Offers made
- Next steps

Use bullet points (-). Do not use asterisks or quotation marks.

Transcript:
{transcript_text}
"""

discussion_prompt = f"""
List key discussion points from the call in bullet points (-) such as:

- Main topics
- Customer needs
- Features mentioned
- Objections

Avoid repeating points already covered in the summary. No asterisks or quotes.

Transcript:
{transcript_text}
"""

objections_prompt = f"""
List all objections raised by the customer. For each, state:

- What the objection was
- Why it was raised
- How the agent responded

Format using bullet points (-). Avoid duplication with earlier sections. Do not use asterisks or quotation marks.

Transcript:
{transcript_text}
"""

actions_prompt = f"""
List follow-up actions the agent should take, like:

- Information to send
- Meeting to schedule
- Concerns to address
- Value to reinforce

Avoid repeating earlier points. Use bullet points (-). No asterisks or quotes.

Transcript:
{transcript_text}
"""

summary = generate_insight(summary_prompt)
discussion_points = generate_insight(discussion_prompt)
objections = generate_insight(objections_prompt)
actions = generate_insight(actions_prompt)

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "AI-Powered Sales Call Insights", ln=True, align="C")
pdf.ln(10)

def add_section(title, content):
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font("Arial", "", 12)
    for line in content.split("\n"):
        if line.strip().startswith("-"):
            text = line.strip().replace("-", "").strip()
            pdf.cell(5)
            pdf.cell(5, 10, "-", ln=False)
            pdf.multi_cell(0, 10, text)
        elif line.strip():
            pdf.multi_cell(0, 10, line.strip())
    pdf.ln(5)

add_section("Call Summary", summary)
add_section("Key Discussion Points", discussion_points)
add_section("Customer Objections", objections)
add_section("Recommended Actions", actions)

output_file = "Detailed_Call_Insights_Report.pdf"
pdf.output(output_file)
print(f"✅ Detailed PDF Generated: {output_file}")
