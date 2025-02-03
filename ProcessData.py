#!/usr/bin/env python
# coding: utf-8

# In[24]:


# Code used to process Trump tweets and rallies.


# In[1]:


from datetime import datetime  # This is the correct import
import numpy as np
import os
import pandas as pd
import re


# In[2]:


BOF = '<|begin_of_text|>'
EOF = '<|end_of_text|>'


# In[3]:


# Tweets


# In[4]:


project_filepath = '$HOME/Documents/Projects/EricBoltonLLMTrump/'
twitter_csv_path = os.path.expandvars(project_filepath + 'tweets_01-08-2021.csv')


# In[5]:


twitter_data = pd.read_csv(twitter_csv_path)


# In[6]:


twitter_data.columns


# In[7]:


twitter_data['date']


# In[8]:


twitter_data['text']


# In[9]:


def is_only_url(text):
    # Pattern to match t.co URLs
    url_pattern = r'^https?://t\.co/\w+$'
    return bool(re.match(url_pattern, text.strip()))


def parse_and_filter_dates_and_urls(df, date_column='date', text_column='text'):
    parsed_dates = []
    filtered_indices = []
    
    for idx, row in df.iterrows():
        date_str = row[date_column]
        text = str(row[text_column])
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            # Check both conditions: date range AND not just a URL
            if (2016 <= date_obj.year <= 2020) and (not is_only_url(text)):  # Actually using is_only_url now
                filtered_indices.append(idx)
                parsed_dates.append(date_obj)
                
        except ValueError as e:
            print(f"Error parsing date: {date_str}")
            continue

    # Create new filtered dataframe
    df_filtered = df.iloc[filtered_indices].copy()
    df_filtered['parsed_date'] = parsed_dates
    
    return df_filtered


# In[10]:


df_filtered = parse_and_filter_dates_and_urls(twitter_data)

# Print summary statistics
print("\nDate range in filtered data:")
print(f"Earliest date: {min(df_filtered['parsed_date'])}")
print(f"Latest date: {max(df_filtered['parsed_date'])}")
print(f"Number of entries: {len(df_filtered)}")

# Optionally, sort by date
df_filtered = df_filtered.sort_values('parsed_date')


# In[11]:


df_filtered


# In[12]:


df_filtered['text'].tail(10)


# In[13]:


df_filtered['content'] = BOF + df_filtered['text'] + EOF
df_filtered['utterance'] = BOF + df_filtered['text'] + EOF


# In[14]:


tweet_processed_filepath = os.path.expandvars(project_filepath + 'trump_tweets_processed.csv')
df_filtered[['content', 'utterance']].to_csv('trump_tweets_processed.csv', index=False)

# Verify the save
print("File saved with shape:", df_filtered[['content', 'utterance']].shape)
print("\nFirst few rows of saved data:")
print(df_filtered[['content', 'utterance']].head())


# In[15]:


# Rallies


# In[16]:


import pandas as pd
import os
import re

# Special tokens
BOF = '<|begin_of_text|>'
EOF = '<|end_of_text|>'

def find_all_sentence_boundaries(text):
    """Find all sentence boundaries in text at once."""
    # Pattern matches: punctuation (.!?) + optional quote + whitespace
    return [m.end() for m in re.finditer(r'[.!?]["\']?\s+', text)]

def chunk_text(text):
    # Find all sentence boundaries once
    boundaries = find_all_sentence_boundaries(text)
    if not boundaries:
        return [f"{BOF}{text}{EOF}"], [f"{BOF}{text}{EOF}"]
    
    chunks = []
    utterances = []
    current_boundary_idx = 0
    
    while current_boundary_idx < len(boundaries):
        # Find the chunk end (approximately 700 characters)
        chunk_start = boundaries[current_boundary_idx - 1] if current_boundary_idx > 0 else 0
        chunk_end_idx = current_boundary_idx
        
        while (chunk_end_idx < len(boundaries) and 
               boundaries[chunk_end_idx] - chunk_start < 700):
            chunk_end_idx += 1
            
        # If we went too far, back up one sentence unless this is our first sentence
        if chunk_end_idx > current_boundary_idx and boundaries[chunk_end_idx - 1] - chunk_start > 800:
            chunk_end_idx -= 1
            
        # Get chunk end position
        chunk_end = boundaries[chunk_end_idx - 1] if chunk_end_idx < len(boundaries) else len(text)
        
        # Extract chunk
        chunk = text[chunk_start:chunk_end].strip()
        
        # Find utterance (last ~100 characters of sentences)
        utterance_start_idx = chunk_end_idx - 1
        while (utterance_start_idx > current_boundary_idx and 
               chunk_end - boundaries[utterance_start_idx - 1] < 100):
            utterance_start_idx -= 1
            
        utterance_start = boundaries[utterance_start_idx - 1] if utterance_start_idx > 0 else chunk_start
        utterance = text[utterance_start:chunk_end].strip()
        
        # Add results
        chunks.append(f"{BOF}{chunk}{EOF}")
        utterances.append(f"{BOF}{utterance}{EOF}")
        
        # Move to next chunk
        current_boundary_idx = chunk_end_idx
    
    return chunks, utterances


# In[17]:


def process_file(file_path):
    """Process a single file and return a DataFrame."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    filename = os.path.basename(file_path)
    content_chunks, utterance_chunks = chunk_text(text)
    
    df = pd.DataFrame({
        'source': [filename] * len(content_chunks),
        'content': content_chunks,
        'utterance': utterance_chunks
    })
    
    return df

def process_directory(directory_path):
    """Process all text files in a directory and return combined DataFrame."""
    all_dataframes = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            df = process_file(file_path)
            all_dataframes.append(df)
    
    final_df = pd.concat(all_dataframes, ignore_index=True)
    return final_df


# In[18]:


all_rally_minipath = 'trump_rally_speeches/'
example_rally_minipath =  all_rally_minipath + 'BattleCreekDec19_2019.txt'
all_rally_path = os.path.expandvars(project_filepath + all_rally_minipath)
example_rally_path = os.path.expandvars(project_filepath + example_rally_minipath)
rally_csv = pd.read_csv(example_rally_path)


# In[19]:


rally_df = process_directory(all_rally_path)


# In[20]:


rally_df


# In[21]:


rally_processed_filepath = os.path.expandvars(project_filepath + 'trump_rallies_processed.csv')
rally_df[['source', 'content', 'utterance']].to_csv('trump_rallies_processed.csv', index=False)

# Verify the save
print("File saved with shape:", rally_df[['source', 'content', 'utterance']].shape)
print("\nFirst few rows of saved data:")
print(rally_df[['source', 'content', 'utterance']].head())


# In[22]:


# Save both


# In[23]:


# Add source column to tweet data
df_filtered['source'] = 'twitter'

# Add binary columns to each dataset
df_filtered['is_tweet'] = True
df_filtered['is_rally'] = False

rally_df['is_tweet'] = False
rally_df['is_rally'] = True

# Combine the datasets
combined_df = pd.concat([df_filtered, rally_df], ignore_index=True)

# Save the combined data
combined_filepath = os.path.expandvars(project_filepath + 'trump_combined_tweets_rallies_processed.csv')
combined_df[['source', 'content', 'utterance', 'is_tweet', 'is_rally']].to_csv('trump_combined_processed.csv', index=False)

# Verify the save
print("File saved with shape:", combined_df[['source', 'content', 'utterance', 'is_tweet', 'is_rally']].shape)
print("\nDistribution of tweets vs rallies:")
print(combined_df[['is_tweet', 'is_rally']].sum())
print("\nFirst few rows of saved data:")
print(combined_df[['source', 'content', 'utterance', 'is_tweet', 'is_rally']].head())


# In[ ]:




