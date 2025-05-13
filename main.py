import argparse
import os
import assemblyai as aai
from fpdf import FPDF
import anthropic
import re

# === Argument Parsing ===
def parse_args():
    parser = argparse.ArgumentParser(description="Generate insights from a sales call audio file.")
    parser.add_argument('audio_file', type=str, help="Path to the audio file (e.g., 'audio/How-to-Overcome-the-Price-Objection.mp3')")
    parser.add_argument('--assemblyai_api_key', type=str, help="AssemblyAI API Key")
    parser.add_argument('--anthropic_api_key', type=str, help="Anthropic API Key")
    return parser.parse_args()

args = parse_args()

# Set API keys from arguments or environment
aai.settings.api_key = args.assemblyai_api_key or os.getenv("ASSEMBLYAI_API_KEY")
client = anthropic.Anthropic(api_key=args.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"))

if not aai.settings.api_key or not client.api_key:
    raise RuntimeError("Both AssemblyAI and Anthropic API keys are required. Set them with --assemblyai_api_key or --anthropic_api_key or in your environment.")

# === AssemblyAI Setup ===
audio_url = args.audio_file  # Use the provided audio file path

config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
transcript = aai.Transcriber(config=config).transcribe(audio_url)

if transcript.status == "error":
    raise RuntimeError(f"Transcription failed: {transcript.error}")

transcript_text = transcript.text

# === Anthropic Setup ===
def clean_text(text):
    text = re.sub(r'[\*"]', '', text).strip()
    text = text.replace("•", "-")  # Convert bullets to hyphens
    return text

def generate_insight(prompt: str) -> str:
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    return clean_text(response.content[0].text.strip())

# === Prompts ===
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

# === Generate Insights ===
summary = generate_insight(summary_prompt)
discussion_points = generate_insight(discussion_prompt)
objections = generate_insight(objections_prompt)
actions = generate_insight(actions_prompt)

# === PDF Generation ===
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
