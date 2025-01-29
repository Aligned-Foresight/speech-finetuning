import argparse
import os
import pandas as pd
from extract_from_conversation_txt import extract_remarks_from_conversation
from extract_from_transcript_txt import extract_remarks_from_transcript
from extract_from_speech_txt import extract_remarks_from_speech
from extract_from_remarks_csv import process_transcript


HARRIS_CONVERSATIONS = [
    ('data/raw/harris1.txt', 'https://www.cbsnews.com/news/vice-president-kamala-harris-face-the-nation-transcript-09-10-2023/'),
    ('data/raw/harris3.txt', 'https://www.cnn.com/2024/08/29/politics/harris-walz-interview-read-transcript/index.html'),
]
HARRIS_SPEECHES = [
    ('data/raw/harris2.txt', 'https://www.nytimes.com/2024/08/23/us/politics/kamala-harris-speech-transcript.html'),
]
HARRIS_TRANSCRIPTS = [
    ('data/raw/harris4.txt', 'https://www.rev.com/blog/transcripts/harris-and-biden-hold-pennsylvania-campaign-event'),
]
HARRIS_DATA = [
    ('data/raw/harris5.csv', 'https://www.kaggle.com/datasets/rmphilly18/vice-presidential-debate-2020-transcript'),
]

TRUMP_CONVERSATIONS = [
    ('data/raw/trump1.txt', 'https://www.cnn.com/2024/06/27/politics/read-biden-trump-debate-rush-transcript/index.html'),
]
TRUMP_TRANSCRIPTS = [
    ('data/raw/trump2.txt', 'https://www.rev.com/blog/transcripts/trump-holds-first-post-debate-rally-in-virginia'),
    ('data/raw/trump3.txt', 'https://www.rev.com/blog/transcripts/trump-rally-in-florida-on-7-09-24'),
    ('data/raw/trump4.txt', 'https://www.rev.com/blog/transcripts/trump-rally-in-grand-rapids-michigan'),
    ('data/raw/trump5.txt', 'https://www.rev.com/blog/transcripts/trump-addresses-national-association-of-black-journalists'),
    ('data/raw/trump6.txt', 'https://www.rev.com/blog/transcripts/trump-and-vance-speak-at-atlanta-rally'),
    ('data/raw/trump7.txt', 'https://www.rev.com/blog/transcripts/trump-holds-news-conference-at-mar-a-lago'),
    ('data/raw/trump8.txt', 'https://www.rev.com/blog/transcripts/vance-and-trump-rally-in-asheboro-nc'),
    ('data/raw/trump9.txt', 'https://www.rev.com/blog/transcripts/donald-trump-speaks-at-the-southern-border'),
    ('data/raw/trump10.txt', 'https://www.rev.com/blog/transcripts/trump-speaks-at-turning-point-rally-in-glendale-arizona'),
    ('data/raw/trump11.txt', 'https://www.rev.com/blog/transcripts/trump-speaks-at-national-guard-conference-in-detroit'),
    ('data/raw/trump12.txt', 'https://www.rev.com/blog/transcripts/trump-speaks-after-appeal-arguement'),
    ('data/raw/trump13.txt', 'https://www.rev.com/blog/transcripts/trump-rally-in-wisconsin'),
    ('data/raw/trump14.txt', 'https://www.rev.com/blog/transcripts/trump-speaks-at-fraternal-order-of-police-meeting'),

]

DEBATE_CONVERSATIONS = [
    ('data/raw/debate1.txt', 'https://abcnews.go.com/Politics/harris-trump-presidential-debate-transcript/story?id=113560542'),
]

VANCE_CONVERSATIONS = [
    ('data/raw/vance1.txt', 'https://www.c-span.org/video/?523437-1/ohio-us-senate-debate'),
]
VANCE_TRANSCRIPTS = [
    ('data/raw/vance2.txt', 'https://www.rev.com/blog/transcripts/vance-rally-in-north-carolina'),
    ('data/raw/vance3.txt', 'https://www.rev.com/blog/transcripts/vance-speaks-at-religious-event'),
]
VANCE_SPEECHES = [
    ('data/raw/vance4.txt', 'https://www.nytimes.com/2024/07/17/us/politics/read-the-transcript-of-jd-vances-convention-speech.html')
]

WALZ_SPEECHES = [
    ('data/raw/walz2.txt', 'https://time.com/7013698/watch-tim-walz-dnc-speech/'),
    ('data/raw/walz3.txt', 'https://mshale.com/2022/04/25/full-transcript-gov-walzs-remarks-state-state-address/'),
]
WALZ_CONVERSATIONS = [
    ('data/raw/walz1.txt', 'https://www.c-span.org/video/?523719-1/minnesota-gubernatorial-debate'),
    ('data/raw/walz4.txt', 'https://www.whitehouse.gov/briefing-room/speeches-remarks/2024/08/06/remarks-by-vice-president-harris-and-governor-tim-walz-at-a-campaign-event/')
]

VICE_DEBATE_TRANSCRIPTS = [
    ('data/raw/debate2.txt', 'https://www.cbsnews.com/news/full-vp-debate-transcript-walz-vance-2024/'),
]

ALL_DATA = (
    HARRIS_DATA + HARRIS_CONVERSATIONS + HARRIS_SPEECHES + HARRIS_TRANSCRIPTS + TRUMP_CONVERSATIONS +
    TRUMP_TRANSCRIPTS + DEBATE_CONVERSATIONS + VANCE_CONVERSATIONS + VANCE_TRANSCRIPTS + VANCE_SPEECHES +
    WALZ_SPEECHES + WALZ_CONVERSATIONS + VICE_DEBATE_TRANSCRIPTS
)


def process_conversations(conversations, speaker, output_file):
    for conversation, source in conversations:
        remarks = extract_remarks_from_conversation(conversation)
        filename = conversation.replace('raw', 'processed').replace('.txt', '.csv')
        df = pd.DataFrame(remarks)
        process_raw_df(df, source, speaker, filename, output_file)


def process_speeches(speeches, speaker, output_file):
    for speech, source in speeches:
        remarks = extract_remarks_from_speech(speech)
        filename = speech.replace('raw', 'processed').replace('.txt', '.csv')
        df = pd.DataFrame(remarks)
        process_raw_df(df, source, speaker, filename, output_file)


def process_transcripts(transcripts, speaker, output_file):
    for transcript, source in transcripts:
        remarks = extract_remarks_from_transcript(transcript)
        filename = transcript.replace('raw', 'processed').replace('.txt', '.csv')
        df = pd.DataFrame(remarks)
        process_raw_df(df, source, speaker, filename, output_file)


def process_data(dataset, speaker, output_file):
    for data, source in dataset:
        filename = data.replace('raw', 'processed').replace('.txt', '.csv')
        df = pd.read_csv(data)
        process_raw_df(df, source, speaker, filename, output_file)

def process_raw_df(df, source, speaker, processed_file, output_file):
    df['source'] = source
    df.to_csv(processed_file, index=False)
    process_transcript(processed_file, os.path.join('data/processed', output_file), speaker=speaker)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select transcripts to process into utterance data.')
    parser.add_argument('--dataset', type=str, help='Transcript dataset to process.')
    parser.add_argument('--output_file', type=str, help='Output file to write processed data to.')
    args = parser.parse_args()

    if args.dataset == 'harris':
        process_conversations(HARRIS_CONVERSATIONS, 'HARRIS', args.output_file)
        process_speeches(HARRIS_SPEECHES, 'HARRIS', args.output_file)
        process_transcripts(HARRIS_TRANSCRIPTS, 'HARRIS', args.output_file)
        process_data(HARRIS_DATA, 'HARRIS', args.output_file)

    elif args.dataset == 'trump':
        process_conversations(TRUMP_CONVERSATIONS, 'TRUMP', args.output_file)
        process_transcripts(TRUMP_TRANSCRIPTS, 'TRUMP', args.output_file)

    elif args.dataset == 'debate':
        process_conversations(DEBATE_CONVERSATIONS, 'HARRIS', args.output_file)
        process_conversations(DEBATE_CONVERSATIONS, 'TRUMP', args.output_file)

    elif args.dataset == 'vance':
        process_conversations(VANCE_CONVERSATIONS, 'VANCE', args.output_file)
        process_transcripts(VANCE_TRANSCRIPTS, 'VANCE', args.output_file)
        process_speeches(VANCE_SPEECHES, 'VANCE', args.output_file)

    elif args.dataset == 'walz':
        process_speeches(WALZ_SPEECHES, 'WALZ', args.output_file)
        process_conversations(WALZ_CONVERSATIONS, 'WALZ', args.output_file)

    elif args.dataset == 'vice_debate':
        process_conversations(VICE_DEBATE_TRANSCRIPTS, 'VANCE', args.output_file)
        process_conversations(VICE_DEBATE_TRANSCRIPTS, 'WALZ', args.output_file)

