import assemblyai as aai
from transformers import T5ForConditionalGeneration, T5Tokenizer
from fpdf import FPDF
import torch

aai.settings.api_key = "8466c5714981458288781b2e7a50f5a2" 
audio_url = "How-to-Overcome-the-Price-Objection.mp3"

config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
transcript = aai.Transcriber(config=config).transcribe(audio_url)

if transcript.status == "error":
    raise RuntimeError(f"Transcription failed: {transcript.error}")

transcript_text = transcript.text

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_insight(prompt: str) -> str:
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).input_ids.to(device)
    output_ids = model.generate(input_ids, max_length=512, temperature=0.8, num_beams=4)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

summary_prompt = f"""
You are an expert summarizer. Write a detailed summary of the sales call, including:
- The purpose of the call.
- All of the customer’s concerns.
- Specific product features discussed (CRM, email integration, etc).
- How the agent handled objections.
- Any offers made and next steps.

Transcript:
{transcript_text}
"""

discussion_prompt = f"""
List comprehensive bullet points about the sales call, focusing on:
- Introduction and goals of the call.
- All customer responses, questions, and objections.
- Detailed agent responses including feature highlights.
- Trial periods, cost negotiation, or scheduling steps.

Transcript:
{transcript_text}
"""

objections_prompt = f"""
Identify each objection raised by the customer in the sales call. For each:
- Explain the reasoning behind the objection.
- Describe how the agent addressed or attempted to resolve it.

Transcript:
{transcript_text}
"""

actions_prompt = f"""
Based on the transcript, suggest detailed follow-up actions the agent should take. Include:
- Any promised materials or demos to send.
- Scheduling requirements or reminders.
- How to readdress unresolved concerns.

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

def add_section(title, content):
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font("Arial", "", 12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line.strip())
    pdf.ln(5)

pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "AI-Powered Sales Call Insights", ln=True, align="C")
pdf.ln(10)

add_section("Call Summary:", summary)
add_section("Key Discussion Points:", discussion_points)
add_section("Customer Objections:", objections)
add_section("Recommended Actions:", actions)

pdf.output("Detailed_Call_Insights_Report.pdf")
print("✅ Detailed PDF Generated: Detailed_Call_Insights_Report.pdf")
