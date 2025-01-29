import spacy
import spacy_transformers

nlp = spacy.load("en_core_web_trf")


def chunk_into_sentences(text):
    # Load the English transformer pipeline
    # Process the text
    doc = nlp(text)

    # Extract sentences
    sentences = [sent.text.strip() for sent in doc.sents]

    return sentences


def extract_remarks_from_speech(input_filename="data/raw/harris2.txt", speaker="HARRIS"):

    # Read the content from the file
    with open(input_filename, "r", encoding="utf-8") as file:
        content = file.read()

    # Chunk the text
    sentences = chunk_into_sentences(content)

    return [{'speaker': speaker, 'text': text.strip()} for text in sentences if text.strip()]
