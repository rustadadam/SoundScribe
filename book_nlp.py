import pandas as pd
import re
import os
from booknlp.booknlp import BookNLP

###########################
# PART 1: Run BookNLP
###########################

# Define model parameters
model_params = {
    "pipeline": "entity,quote,supersense,event,coref",
    "model": "big"  # You can also try "small" if accuracy improves
}

# Initialize BookNLP with the English language model and parameters
booknlp = BookNLP("en", model_params)

# Define input and output paths for BookNLP processing
input_file = "/yunity/arusty/SoundScribe/text_files/Legacy of the Lost.txt"
output_dir_bnlp = "/yunity/arusty/SoundScribe/book_files"
book_id = "lotl"
original_text_file = "/yunity/arusty/SoundScribe/text_files/Legacy of the Lost.txt"


# Process the book (this generates files in output_dir_bnlp)
#booknlp.process(input_file, output_dir_bnlp, book_id)

###########################
# PART 2: Build Coreference Mapping from Entities
###########################

# File paths for BookNLP outputs
entities_file = f"{output_dir_bnlp}/{book_id}.entities"   # Entities file from BookNLP
quotes_file   = f"{output_dir_bnlp}/{book_id}.quotes"       # Quotes file from BookNLP

# Load the entities file (assumes tab-separated and with headers or consistent column order)
# Expected columns: COREF, start_token, end_token, prop, cat, text
entities_df = pd.read_csv(entities_file, sep="\t")

# Filter for person entities (cat == "PER")
person_entities = entities_df[entities_df["cat"] == "PER"].copy()
# Sort by start_token to process in natural order
person_entities = person_entities.sort_values(by=["start_token"])

# Build a mapping: For each unique COREF, collect all mentions.
from collections import defaultdict

coref_mentions = defaultdict(list)
for _, row in person_entities.iterrows():
    entity_id = str(row["COREF"])  # Use COREF as the unique ID
    mention_text = row["text"]
    coref_mentions[entity_id].append(mention_text)

# Now, build a refined mapping that picks the best (most frequent proper) name per entity.
resolved_map = {}
for entity_id, mentions in coref_mentions.items():
    # Filter for proper names (using istitle() as a heuristic)
    proper_names = [str(m) for m in mentions if isinstance(m, str) and m.istitle()]
    if proper_names:
        # Use the most frequent proper name
        resolved_map[entity_id] = max(set(proper_names), key=proper_names.count)
    else:
        # Fall back to the most frequent mention overall
        resolved_map[entity_id] = max(set(mentions), key=mentions.count)

print("Final Coreference Mapping:")
print(resolved_map)

###########################
# PART 3: Process Quotes and Build Output Files
###########################

# Load the quotes file.
# Adjust the separator and header as needed.
# Here we assume the quotes file has a header with at least columns:
# "quote", "char_id", "quote_start", "quote_end"
quotes_df = pd.read_csv(quotes_file, sep="\t", header=0, on_bad_lines='warn')

# Convert char_id to string for mapping
quotes_df["char_id"] = quotes_df["char_id"].astype(str)

# Map char_id to resolved character names using our refined mapping.
quotes_df["Resolved Speaker"] = quotes_df["char_id"].map(resolved_map)

# (Optional) Define a further refinement function in case the resolved name is still a pronoun.
def refine_speaker(speaker, coref_map):
    pronouns = {"he", "his", "she", "her", "they", "their", "my"}
    if speaker and speaker.lower() in pronouns:
        return coref_map.get(speaker.lower(), speaker)
    return speaker

# If you have additional coreference information, you could update the speakers.
# For now, we'll use the resolved_map result directly.
quotes_df["Resolved Speaker"] = quotes_df["Resolved Speaker"].fillna("Unknown")

# ----------------------
# File 1: Create Character Dialogue File
# ----------------------
# Build a dictionary mapping each speaker to a list of their quotes.
character_quotes = {}
for _, row in quotes_df.iterrows():
    speaker = row["Resolved Speaker"]
    quote = row["quote"]
    if speaker not in character_quotes:
        character_quotes[speaker] = []
    character_quotes[speaker].append(f'"{quote}"')

# Define output directory for our files
output_dir = f"book-text-info/{book_id}/"
os.makedirs(output_dir, exist_ok=True)
character_dialogue_file = f"{output_dir}{book_id}-character-dialogue.txt"

# Write the character dialogue file.
with open(character_dialogue_file, "w", encoding="utf-8") as f:
    for character, quotes in character_quotes.items():
        f.write(f"{character}: {' '.join(quotes)}\n")

# ----------------------
# File 2: Create Annotated Text File
# ----------------------
# Read the original text.
with open(original_text_file, "r", encoding="utf-8") as f:
    text = f.read()

# We'll use a regex-based method to find quotes in the text.
# We assume quotes are enclosed in either straight or smart quotes.
pattern = r'(["“][^"”]+["”])'

# Extract the list of resolved speakers from the quotes file, in order.
# (We assume that the quotes appear in the text in the same order as in the quotes_df.)
resolved_speakers = quotes_df["Resolved Speaker"].tolist()

# Create an iterator for the resolved speakers.
speaker_iter = iter(resolved_speakers)

def replacer(match):
    try:
        speaker = next(speaker_iter)
    except StopIteration:
        speaker = "Unknown"
    matched_quote = match.group(0)
    return f"</{speaker}> {matched_quote}"

annotated_text = re.sub(pattern, replacer, text, count=0)

audio_text_file = f"{output_dir}{book_id}-book-audio-text.txt"
with open(audio_text_file, "w", encoding="utf-8") as f:
    f.write(annotated_text)

print("Files saved successfully!")
