import base64
import requests
import json
import re
from PIL import Image
import io

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen2-vl-7b-instruct" 

def encode_image(image_path: str) -> str:
    """Resizes and converts an image file to a base64 string."""
    try:
        with Image.open(image_path) as img:
            # 1. Resize to prevent timeouts: max width/height of 1024px
            img.thumbnail((1024, 1024))
            
            # 2. Handle transparency (RGBA) if present
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # 3. Save to buffer as JPEG
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            
            # 4. Return as base64 string
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
            
    except FileNotFoundError:
        print(f"❌ Error: File not found at {image_path}")
        return ""
    except Exception as e:
        print(f"❌ Error encoding image: {e}")
        return ""

def parse_json_from_response(content: str):
    """Removes markdown code blocks and parses result into a dictionary."""
    # Extracts content between ```json and ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
    clean_content = match.group(1) if match else content
    
    try:
        return json.loads(clean_content.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": content}

def extract_invoice_json(image_path: str, prompt: str):
    """Sends image and prompt to the local VLM server with 5-minute timeout."""
    image_base64 = encode_image(image_path)
    if not image_base64:
        return None

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ],
        "temperature": 0 
    }

    try:
        # Timeout set to 300 seconds (5 minutes) for local inference
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            raw_text = result["choices"][0]["message"]["content"]
            return parse_json_from_response(raw_text)
        
        return {"error": "Unexpected response format"}

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return None