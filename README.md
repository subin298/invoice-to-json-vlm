# Invoice to JSON with a Local Vision Language Model

I built this to see how far a small vision model running on my own laptop could get at reading invoices. You give it a photo or scan of an invoice, and it hands back a clean JSON file with the vendor, dates, totals and line items.

Everything runs locally through LM Studio, so there are no API keys, no costs, and the invoices never leave my machine.

---

## Why I made this

Most invoice parsers I looked at use OCR plus a pile of rules, and they fall apart the moment a layout changes. A vision-language model looks at the page the way a person does, so I wanted to try Qwen2-VL-7B on it and see whether it could handle different invoice formats without any templates.

It mostly works. It also taught me a lot about where small models slip up, which I've written down in the limitations below.

---

## How it works

1. You drop an invoice image into `samples/`.
2. The script shrinks the image, converts it to JPEG and base64-encodes it.
3. It sends the image and a prompt to Qwen2-VL running in LM Studio.
4. The model replies with JSON, and the script cleans it up (models love wrapping JSON in markdown fences).
5. I force the result into a fixed set of 13 fields, in a fixed order. If the model skips a field, it gets an empty value. If it invents an extra one, it gets dropped.
6. The result is saved in `output/`, named after the image. `invoice1.jpeg` becomes `invoice1.json`.

I enforce the schema in code instead of trusting the prompt alone, because a 7B model doesn't always follow formatting instructions, and I wanted the output to look the same every time.

---

## Built with

- Python
- LM Studio (local server with an OpenAI-style API)
- Qwen2-VL-7B-Instruct (GGUF)
- `requests`, `Pillow`, `python-dotenv`

---

## Project layout

```
project-root/
├── samples/            # put your invoice images here
├── output/             # JSON results land here (created automatically)
├── requirements.txt
├── README.md
└── src/
    ├── main.py         # entry point, runs everything and enforces the schema
    ├── vlm_client.py   # image prep, talks to LM Studio, parses the reply
    └── prompt.py       # the prompt and JSON template the model sees
```

`main.py` looks for `../samples` and `../output`, so it needs to sit one folder below them.

---

## Getting it running

**1. Set up LM Studio**

- Install [LM Studio](https://lmstudio.ai/).
- Download **Qwen2-VL-7B-Instruct (GGUF)** and load it.
- Start the local server. By default it runs at `http://localhost:1234`.

**2. Install the Python packages**

```bash
pip install -r requirements.txt
```

**3. Check the settings**

At the top of `src/vlm_client.py`:

```python
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen2-vl-7b-instruct"
```

If LM Studio shows a different name for your model, change `MODEL_NAME` to match.

**4. Run it**

Put an invoice in `samples/`, then:

```bash
cd src
python main.py invoice1.jpeg
```

Your JSON will be at `output/invoice1.json`.

---

## What you get back

```json
{
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
    "line_items": [
        {
            "item": "",
            "description": "",
            "quantity": "",
            "unit_price": "",
            "amount": ""
        }
    ]
}
```

---

## Things I know aren't great yet

I'd rather be upfront about these than have you discover them:

- **Small text suffers.** I shrink images to 1024px so inference doesn't time out, but dense invoices can lose detail. A higher limit might help, at the cost of speed.
- **Everything is a string.** Amounts and dates come back as the model read them, with no cleanup and no check that subtotal plus tax equals the total.
- **Empty is ambiguous.** A blank field could mean "not on the invoice" or "the model missed it."
- **Weak error handling.** If LM Studio isn't running or the model returns something unparseable, the script can crash or save a mostly empty file without saying why.
- **One image at a time.** No batch mode, and no multi-page PDFs yet.
- **Speed depends on your hardware.** A 7B model on a laptop is not fast.

---

## What I want to do next

- [ ] Fail loudly when the model call or JSON parsing goes wrong
- [ ] Check that the totals add up
- [ ] Use `null` for missing fields and real numbers for amounts
- [ ] Normalize dates to `YYYY-MM-DD`
- [ ] Move the URL and model name into a `.env` file
- [ ] Process a whole folder at once
- [ ] Support PDF invoices
- [ ] Define the schema in one place instead of two
- [ ] Add an example invoice and its output to this README

---

## About me

I'm Subin, a fresher working on AI/ML and computer vision. This is one of my hands-on projects while I learn by building. You can find more on my GitHub: [github.com/subin298](https://github.com/subin298)
