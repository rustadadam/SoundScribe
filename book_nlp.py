from booknlp.booknlp import BookNLP

# Define model parameters
model_params = {
    "pipeline": "entity,quote,supersense,event,coref",
    "model": "big" # Small may be an improvement in accuracy too!
}

# Initialize BookNLP with the English language model and parameters
booknlp = BookNLP("en", model_params)

# Define input and output paths
input_file = "/yunity/arusty/SoundScribe/text_files/chapter4.txt"
output_dir = "/yunity/arusty/SoundScribe/book_files"
book_id = "lotl-chapter4"

# Process the book
booknlp.process(input_file, output_dir, book_id)

"""-------------------------  BUILD FILES   -------------------------"""
import pandas as pd
import re
import os


def refine_speaker(speaker, coref_mapping):
    # If the speaker is a pronoun, try to look up a better name
    pronouns = {"he", "his", "she", "her", "they", "their", "my"}
    if speaker.lower() in pronouns:
        # Look up a better name from the coreference mapping; for example:
        return coref_mapping.get(speaker.lower(), speaker)
    return speaker


# File paths
original_text_file = "/yunity/arusty/SoundScribe/text_files/chapter4.txt"  # Replace with your actual input text file
book_title = "lotl-chapter4"  # Replace with your actual book title
output_dir = "book-text-info/" + book_title + "/" # Adjust if needed
audio_text_file = output_dir + book_title + "-book-audio-text.txt"
character_dialogue_file = output_dir + book_title + "-character-dialogue.txt"
quotes_file = "book_files/" + book_title + ".quotes"  # Replace with your actual quotes file
entities_file = "book_files/" + book_title + ".entities"  # Replace with your actual quotes file

# ----------------------
# Step 1: Build the Resolved Mapping from Entities
# ----------------------
# Load the entities file (assuming it's tab-separated)
entities_df = pd.read_csv(entities_file, sep="\t")

# Filter for person entities (where 'cat' equals "PER")
person_entities = entities_df[entities_df["cat"] == "PER"].copy()

# Sort entities by token position if needed (here using 'start_token')
person_entities = person_entities.sort_values(by=["start_token"])

# Build an initial mapping: use the 'COREF' column as the key and the 'text' column as the name.
# We convert the COREF value to a string.
initial_map = {}
for _, row in person_entities.iterrows():
    entity_id = str(row["COREF"])
    entity_text = row["text"]
    # Prefer proper names (if entity_text is title-cased) over pronouns or descriptions
    if entity_id in initial_map:
        if not entity_text.istitle():
            continue  # Skip if we already have a proper name for this ID
    initial_map[entity_id] = entity_text

# Optionally, you can print the initial mapping for debugging:
print("Initial Mapping:")
print(initial_map)

# Now, if you wish to backfill or override less informative labels with later, better ones,
# you can simply use the initial_map as your resolved mapping.
resolved_map = initial_map

# ----------------------
# Step 2: Load Quotes and Map Speaker IDs to Resolved Names
# ----------------------
# Load quotes file; assume it's tab-separated with two columns: Quote and char_id.
quotes_df = pd.read_csv(quotes_file, sep="\t", header=0)

# Convert char_id to string for proper matching
quotes_df["char_id"] = quotes_df["char_id"].astype(str)

# Map char_id to real character names using our resolved_map.
quotes_df["Resolved Speaker"] = quotes_df["char_id"].map(resolved_map)
quotes_df["Resolved Speaker"] = quotes_df["Resolved Speaker"].apply(lambda sp: refine_speaker(sp, coref_mapping))


# Optionally, check if there are any unmapped IDs (should be empty if all mapped correctly)
unmapped = quotes_df[quotes_df["Resolved Speaker"].isna()]
print("Unmapped Speaker IDs:", unmapped["char_id"].unique())

# ----------------------
# Step 3: Create File 1 – Character Dialogue File
# ----------------------
# Build a dictionary mapping each resolved speaker to a list of their quotes.
character_quotes = {}
for _, row in quotes_df.iterrows():
    speaker = row["Resolved Speaker"] if pd.notna(row["Resolved Speaker"]) else "Unknown"
    quote = row["quote"]
    if speaker not in character_quotes:
        character_quotes[speaker] = []
    character_quotes[speaker].append(f'{quote} | ')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Write the character dialogue file
with open(character_dialogue_file, "w", encoding="utf-8") as f:
    for character, quotes in character_quotes.items():
        f.write(f"{character}: {' '.join(quotes)}\n")

# Ensure that the quotes are processed in order of their starting offsets
quotes_df = quotes_df.sort_values(by="quote_start")

# Extract the list of resolved speakers and quotes
resolved_speakers = quotes_df["Resolved Speaker"].tolist()
quote_texts = quotes_df["quote"].tolist()

# For debugging: print the list of speakers
print("Resolved Speakers:", resolved_speakers)

# Read the original text
with open(original_text_file, "r", encoding="utf-8") as f:
    text = f.read()

# Define a regex pattern to match quotes (both straight and smart quotes)
pattern = r'(["“][^"”]+["”])'

# Create iterators for the resolved speakers and (optionally) the quote texts
speaker_iter = iter(resolved_speakers)
# If you want to compare the matched quote with the expected one, you can also use quote_iter:
# quote_iter = iter(quote_texts)

def replacer(match):
    # Get the next speaker from our iterator (if available)
    try:
        speaker = next(speaker_iter)
    except StopIteration:
        speaker = "Unknown"
    # Matched quote (including the surrounding quotes)
    matched_quote = match.group(0)
    # Return the speaker tag followed by the matched quote
    return f"</{speaker}> {matched_quote}"

# Use re.sub with our replacer function
annotated_text = re.sub(pattern, replacer, text, count=0)

# Save the annotated text to the output file
os.makedirs(os.path.dirname(audio_text_file), exist_ok=True)
with open(audio_text_file, "w", encoding="utf-8") as f:
    f.write(annotated_text)

print("Annotated text file saved successfully!")