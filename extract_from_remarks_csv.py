import os
import os.path

import pandas as pd
from definitions import LLAMA_MAX_TOKENS
from transformers import AutoTokenizer
from huggingface_hub import login
from dotenv import load_dotenv

# Initialize the Llama tokenizer
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
login(HF_TOKEN)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

bos = '<|begin_of_text|>'
eos = '<|end_of_text|>'


def get_token_length(text):
    return len(tokenizer.encode(text, add_special_tokens=False))


def cumsum_rows(df):
    df['chunks'] = df.text.apply(lambda x: [x.strip()])
    df['chunk_speakers'] = df.speaker.apply(lambda x: [x])
    df['chunk_tokens'] = df.text.apply(lambda x: [get_token_length(x)])

    df['chunks'] = df.chunks.cumsum()
    df['chunk_tokens'] = df.chunk_tokens.cumsum()

    def cut_row(row):
        while sum(row.chunk_tokens) + 3 > LLAMA_MAX_TOKENS:
            row['chunks'] = row.chunks[1:]
            row['chunk_tokens'] = row.chunk_tokens[1:]

        return row

    df = df.apply(cut_row, axis=1)

    df['utterance'] = df.apply(
        lambda row: f'{row.speaker.upper()}: {row.text}' if len(row.chunks) == 1 else f'{row.text}', axis=1)
    df['content'] = df.apply(lambda row: f'{row.speaker.upper()}: {" ".join(row.chunks)}', axis=1)
    df['chunks'] = df.apply(lambda row: [f'{row.speaker.upper()}: {row.chunks[0]}', *row.chunks[1:]], axis=1)
    df['chunks'] = df.chunks.apply(lambda x: [*x[:-1], f'{x[-1]}'])
    df['chunk_tokens'] = df.apply(lambda row: [get_token_length(x) for x in row.chunks], axis=1)

    return df


def join_speaker_rows(df):
    # Add a column to indicate speaker changes
    df['speaker_change'] = df['speaker'] != df['speaker'].shift()
    df['group'] = df.speaker_change.cumsum()
    df['chunks'] = df.text.apply(lambda x: [x.strip()])
    df['chunk_speakers'] = df.speaker.apply(lambda x: [x])
    df['chunk_tokens'] = df.text.apply(lambda x: [get_token_length(x)])

    # Combine consecutive rows with the same speaker
    df = df.groupby('group').agg({
        'speaker': 'first',
        'source': 'first',
        'chunks': 'sum',
        'chunk_tokens': 'sum',
        'chunk_speakers': 'sum',
        'text': ' '.join,
    })

    # Add speaker labels to the text
    df['text'] = df.apply(lambda row: f'{row.speaker.upper()}: {row.text}\n', axis=1)
    df['chunks'] = df.apply(lambda row: [f'{row.speaker.upper()}: {row.chunks[0]}', *row.chunks[1:]], axis=1)
    df['chunks'] = df.chunks.apply(lambda x: [*x[:-1], f'{x[-1]}\n'])
    df['chunk_tokens'] = df.apply(lambda row: [get_token_length(x) for x in row.chunks], axis=1)

    return df


def split_row(row, max_tokens=LLAMA_MAX_TOKENS):
    new_rows = []

    while row['chunks']:
        new_row = {**row, 'chunks': [], 'chunk_tokens': [], 'chunk_speakers': [], 'text': ''}
        while row['chunks'] and sum(new_row['chunk_tokens']) + row['chunk_tokens'][0] + 2 <= max_tokens:
            new_row['chunks'].append(row['chunks'].pop(0))
            new_row['chunk_tokens'].append(row['chunk_tokens'].pop(0))
            new_row['chunk_speakers'].append(row['chunk_speakers'].pop(0))
        new_row['text'] = ' '.join(new_row['chunks']).strip() + '\n'
        new_rows.append(new_row)

    return new_rows


def split_rows(df, max_tokens=LLAMA_MAX_TOKENS):
    rows = []
    for row in df.to_dict(orient='records'):

        if sum(row['chunk_tokens']) + 2 <= max_tokens:
            rows.append(row)
        else:
            rows.extend(split_row(row, max_tokens=max_tokens))

    df = pd.DataFrame(rows)
    assert df.chunk_tokens.apply(lambda x: all(t < max_tokens for t in x)).all()
    return df


def build_content(df, max_tokens=LLAMA_MAX_TOKENS):
    df['content'] = df.text.fillna('').cumsum()
    df['content_tokens'] = df.content.apply(lambda x: get_token_length(x) + 2)
    df['content_chunks'] = df.chunks.apply(lambda x: x if isinstance(x, list) else []).cumsum()
    df['content_chunk_tokens'] = df.chunk_tokens.apply(lambda x: x if isinstance(x, list) else []).cumsum()
    df['content_chunk_speakers'] = df.chunk_speakers.apply(lambda x: x if isinstance(x, list) else []).cumsum()
    df = pd.DataFrame([cut_content(row, max_tokens=max_tokens) if row['content_tokens'] > max_tokens else row
                       for row in df.to_dict(orient='records')])
    return df


def cut_content(row, max_tokens=LLAMA_MAX_TOKENS):
    new_row = {**row, 'content_chunks': [], 'content_chunk_tokens': [], 'content_chunk_speakers': []}

    while sum(new_row['content_chunk_tokens']) + row['content_chunk_tokens'][-1] + 2 <= max_tokens:
        new_row['content_chunks'] = [row['content_chunks'].pop(-1)] + new_row['content_chunks']
        new_row['content_chunk_tokens'] = [row['content_chunk_tokens'].pop(-1)] + new_row['content_chunk_tokens']
        new_row['content_chunk_speakers'] = [row['content_chunk_speakers'].pop(-1)] + new_row['content_chunk_speakers']

    new_row['content'] = ' '.join(new_row['content_chunks'])
    if not new_row['content'].startswith(new_row['content_chunk_speakers'][0].upper()):
        new_row['content'] = f'{new_row["content_chunk_speakers"][0].upper()}: {new_row["content"]}'

    return new_row


def process_transcript(input_file, output_file, speaker='HARRIS', max_tokens=LLAMA_MAX_TOKENS, speech_mode=False):
    target_cols = ['speaker', 'content', 'content_tokens', 'utterance', 'utterance_tokens', 'full_text', 'source']

    df = pd.read_csv(input_file)
    df['speaker'] = df.speaker.fillna('None')

    if speech_mode:
        # Ensure speakers are consistent
        final_df = cumsum_rows(df)
    else:
        # Ensure speakers alternate
        joined_df = join_speaker_rows(df)
        split_df = split_rows(joined_df, max_tokens=max_tokens)
        final_df = build_content(split_df, max_tokens=max_tokens)

    if speech_mode:
        final_df['content'] = final_df.apply(lambda row: f'{bos}{row.content}{eos}', axis=1)
        final_df['content_tokens'] = final_df.content.apply(get_token_length)
        final_df['utterance'] = final_df.apply(
            lambda row: f'{bos}{row.utterance}', axis=1
        )
    else:
        final_df['content'] = final_df.apply(lambda row: f'{bos}{row.content}{eos}', axis=1)
        final_df['content_tokens'] = final_df.content.apply(get_token_length)
        final_df['utterance'] = final_df.apply(
            lambda row: f'{bos}{row.text}{eos}'
            if row.text.startswith(row.speaker.upper())
            else f'{bos}{row.speaker.upper()}: {row.text}{eos}', axis=1
        )
    final_df['utterance_tokens'] = final_df.utterance.apply(get_token_length)
    final_df['full_text'] = ' '.join(final_df.text.fillna(''))

    if speaker:
        final_df = final_df[final_df.speaker.str.contains(speaker, case=False) & ~final_df.speaker.str.contains('jr.', case=False)]

    if os.path.exists(output_file):
        final_df[target_cols].to_csv(output_file, mode='a', header=False, index=False)
    else:
        final_df[target_cols].to_csv(output_file, index=False)
