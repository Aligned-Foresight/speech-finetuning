import re


def parse_debate(transcript):
    # Split the transcript into segments based on speaker changes
    segments = re.split(r'([A-Z\s]+:)', transcript)

    parsed_debate = ""
    current_speaker = ""

    for i in range(1, len(segments), 2):
        speaker = segments[i].strip().rstrip(':')
        content = segments[i + 1].strip()

        # Combine consecutive segments from the same speaker
        if speaker == current_speaker:
            parsed_debate += " " + content
        else:
            if current_speaker:
                parsed_debate += "\n\n"
            parsed_debate += f"{speaker}: {content}"
            current_speaker = speaker

    return parsed_debate


parsed_debate = parse_debate(transcript)
print(parsed_debate)