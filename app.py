from flask import Flask, render_template, request, jsonify
from markupsafe import escape
import os
import re

app = Flask(__name__)

# ─── Word-level English→Maithili dictionary ────────────────────────────────────
english_to_maithili = {
    "?": "?",
    "घर": "House",
    "पानी": "Water",
    "रात": "Night",
    "दिन": "Day",
    "आदमी": "Man",
    "महिला": "Woman",
    "बच्चा": "Child",
    "सपना": "Dream",
    "खुशी": "Happiness",
    "दुःख": "Sadness",
    "पुस्तक": "Book",
    "कपड़ा": "Clothes",
    "रोटी": "Bread",
    "फल": "Fruit",
    "सपना": "Dream",
}

# ─── Build path to the sentence-level dataset ───────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "maithalidataset.txt")

# ─── Load sentence-level translations from the TSV file ────────────────────────
def load_sentence_dictionary(file_path):
    sentence_dict = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    maithili, english = parts
                    sentence_dict[english.strip().lower()] = maithili.strip()
        print(f"Loaded {len(sentence_dict)} sentence-level translations from {file_path}")
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}")
    return sentence_dict

sentence_translation = load_sentence_dictionary(DATA_PATH)

# ─── Optional tuple-based templates for common patterns ────────────────────────
sentence_templates = {
    ("what", "is", "your", "name"): "तेरो नाँव के हो?",
    ("how", "are", "you"): "तूँ कते छी?",
    ("where", "are", "you"): "तूँ कतय छी?",
    ("what", "is", "this"): "ई के हो?",
}

# ─── Helper: Split paragraph into individual sentences ─────────────────────────
def split_into_sentences(text):
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    return sentence_endings.split(text.strip())

# ─── Translation function supporting multiple sentences ────────────────────────
def translate_to_maithili(paragraph):
    sentences = split_into_sentences(paragraph)
    translated_sentences = []

    for sentence in sentences:
        sentence_lower = sentence.lower().strip()

        # 1) Direct sentence match
        if sentence_lower in sentence_translation:
            translated = sentence_translation[sentence_lower]
        else:
            # 2) Tuple-template match
            words_tuple = tuple(sentence_lower.split())
            if words_tuple in sentence_templates:
                translated = sentence_templates[words_tuple]
            else:
                # 3) Word-by-word fallback
                translated_words = [
                    english_to_maithili.get(word, word)
                    for word in sentence_lower.split()
                ]
                translated = " ".join(translated_words)
        translated_sentences.append(translated)

    return " ".join(translated_sentences)

# ─── Flask Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json or {}
    english_text = data.get("text", "")
    maithili_text = translate_to_maithili(english_text)
    return jsonify({"translation": maithili_text})

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5009, debug=True)
