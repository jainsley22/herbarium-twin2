
import json
import os

from google import genai
from google.genai import types


# Gemini configuration - change if using a different model
GEMINI_MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        api_version="v1beta"
    )
)


def load_image_bytes(image_path):
    """Read raw image bytes from disk."""
    with open(image_path, "rb") as image_file:
        return image_file.read()


def analyze_box_images(image_paths):
    """Analyze herbarium box images using Gemini.

    Returns:
        dictionary of AI-generated metadata
    """

    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is missing.")

    image_parts = []

    for path in image_paths:
        image_bytes = load_image_bytes(path)

        image_parts.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            )
        )

    prompt = """
You are helping digitize a museum herbarium collection.

Analyze the provided herbarium box images.

Return ONLY valid JSON.

Use this format:

{
    "collection_area": "",
    "material_type": "",
    "estimated_packet_count": "",
    "taxonomic_clues": "",
    "geographic_clues": "",
    "collector_clues": "",
    "condition": "",
    "processing_status": "",
    "priority": "",
    "ai_summary": "",
    "ai_confidence_notes": ""
}

Rules:

- Do not invent information.
- If something cannot be determined, say "Unknown".
- Look for:
  - labels
  - specimen packets
  - handwritten notes
  - collector names
  - locations
  - dates
  - taxonomic information
  - specimen condition

Keep responses concise.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, *image_parts],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    result_text = (response.text or "").strip()

    try:
        result = json.loads(result_text)

    except json.JSONDecodeError:
        result = {
            "collection_area": "Unknown",
            "material_type": "Unknown",
            "estimated_packet_count": "Unknown",
            "taxonomic_clues": "Unknown",
            "geographic_clues": "Unknown",
            "collector_clues": "Unknown",
            "condition": "Unknown",
            "processing_status": "Unknown",
            "priority": "Unknown",
            "ai_summary": result_text or "No response received.",
            "ai_confidence_notes": "AI output was not formatted correctly.",
        }

    return result
