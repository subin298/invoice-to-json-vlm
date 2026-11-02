import os
import sys
import json
from vlm_client import extract_invoice_json
from prompt import JSON_SCHEMA


def main():
    # 1️⃣ Check argument
    if len(sys.argv) < 2:
        print("❌ Error: No filename provided.")
        print("Usage: python main.py image_name.jpeg")
        return

    input_file = sys.argv[1]

    # 2️⃣ Build full image path (samples folder)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH = os.path.normpath(
        os.path.join(BASE_DIR, "..", "samples", input_file)
    )

    if not os.path.exists(IMAGE_PATH):
        print("❌ Image not found:", IMAGE_PATH)
        return

    print(f"🔍 Processing file: {input_file}")

    # 3️⃣ Build prompt
    PROMPT = f"""
You are an AI system that extracts structured data from invoice images.

{JSON_SCHEMA}
"""

    # 4️⃣ Call VLM
    result = extract_invoice_json(IMAGE_PATH, PROMPT)

    print("\nRAW RESPONSE FROM LM STUDIO:\n")
    print(result)

    # 5️⃣ Enforce Ordered Schema
    ordered_schema = {
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "vendor_name": "",
        "vendor_address": "",
        "bill_to": "",
        "ship_to": "",
        "sub_total": "",
        "tax_rate": "",
        "tax_amount": "",
        "total_amount": "",
        "balance_due": "",
        "line_items": []
    }

    ordered_json = {}

    for key in ordered_schema:
        ordered_json[key] = result.get(key, ordered_schema[key])

    json_data = ordered_json

    # 6️⃣ Create output folder
    OUTPUT_DIR = os.path.normpath(
        os.path.join(BASE_DIR, "..", "output")
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 7️⃣ Save JSON using invoice filename
    file_name_without_ext = os.path.splitext(input_file)[0]
    output_file_path = os.path.join(
        OUTPUT_DIR,
        f"{file_name_without_ext}.json"
    )

    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    print("\n✅ JSON saved to:", output_file_path)


if __name__ == "__main__":
    main()
