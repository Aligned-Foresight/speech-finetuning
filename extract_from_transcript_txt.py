import re

from extract_from_speech_txt import chunk_into_sentences


def clean_text(text, speaker):
    text = re.sub(r'(\[inaudible\s|\()(\d{2}(:\d{2})?:\d{2})(\)|\])', '', text).strip()
    text = re.sub(r'(\. \.\s?)+', '. ', text).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.removeprefix(f'{speaker}: ')
    return text


def chunk_text(text):
    # Split the text into segments based on speaker labels
    segments = re.split('\n\n', text)

    rows = []
    current_speaker = ""

    for segment in segments:
        # Extract speaker, initial timestamp, and content
        segment = segment.strip()
        match = re.match(r'(.+(?:\s+\w+)*)\s+(\(\d{2}(:\d{2})?:\d{2}\):)(.*)', segment, re.DOTALL)
        if match:
            speaker, timestamp, _, content = match.groups()
            current_speaker = speaker
        else:
            content = segment

        content = clean_text(content, current_speaker)
        if content:
            sentences = chunk_into_sentences(content)
            rows.extend({'speaker': current_speaker, 'text': text} for text in sentences)

    return rows


def extract_remarks_from_transcript(input_filename="data/raw/harris4.txt"):
    # Read the content from the file
    with open(input_filename, "r", encoding="utf-8") as file:
        content = file.read()

    # Chunk the text
    remarks = list(chunk_text(content))

    return remarks
