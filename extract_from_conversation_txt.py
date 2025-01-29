import re


def extract_remarks_from_conversation(input_filename):
    with open(input_filename, 'r') as f:
        lines = f.readlines()

    current_speaker = ""
    current_remark = ""
    rows = []

    for line in lines:
        if not line:
            continue

        try:
            speaker, text = line.split(":", 1)
            if current_speaker == speaker:
                current_remark += " " + text.strip()
            elif current_remark:
                rows.append({'speaker': current_speaker, 'text': current_remark.strip()})
                current_remark = text.strip()
            else:
                current_remark = text.strip()
        except ValueError:
            speaker = current_speaker
            current_remark += " " + line.strip()

        current_speaker = speaker

    rows.append({'speaker': current_speaker, 'text': current_remark.strip()})
    return rows
