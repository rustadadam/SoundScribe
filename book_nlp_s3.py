import pandas as pd
import re
import os
import boto3
from booknlp.booknlp import BookNLP
from collections import defaultdict

###########################
# CONFIGURATION
###########################
# S3 bucket names
import sys

# Ensure an S3 key argument is passed when running the script
if len(sys.argv) < 2:
    print("Usage: python book_nlp.py <s3_key>")
    sys.exit(1)

# Get the S3 key from the command-line argument
s3_input_key = sys.argv[1]

# S3 bucket names
S3_INPUT_BUCKET = "raw-book"  # Source bucket where text files are uploaded
S3_OUTPUT_BUCKET = "book-text-info"  # Output bucket where processed files are saved

print(f"Processing file from S3: {s3_input_key}")

# Local paths (we'll use /tmp/ for temporary storage on EC2)
local_input_file = f"/home/ec2-user/{os.path.basename(s3_input_key)}"
# BookNLP output directory (local)
output_dir_bnlp = f"/home/ec2-user/booknlp_output"
# Book ID: use the file name (without extension)
book_id = os.path.splitext(os.path.basename(local_input_file))[0]

# Directory for final processed outputs
output_dir = f"/home/ec2-user/book-text-info/{book_id}/"
os.makedirs(output_dir, exist_ok=True)

# ----------------------
# AWS S3 Client Setup
# ----------------------
s3_client = boto3.client("s3")

def download_from_s3(s3_bucket, s3_key, local_path):
    s3_client.download_file(s3_bucket, s3_key, local_path)
    print(f"Downloaded {s3_key} from bucket {s3_bucket} to {local_path}")

def upload_to_s3(local_path, s3_bucket, s3_key):
    s3_client.upload_file(local_path, s3_bucket, s3_key)
    print(f"Uploaded {local_path} to bucket {s3_bucket} with key {s3_key}")

###########################
# PART 1: Download Input and Run BookNLP
###########################
# Download the raw input file from S3
download_from_s3(S3_INPUT_BUCKET, s3_input_key, local_input_file)

# Define model parameters for BookNLP
model_params = {
    "pipeline": "entity,quote,coref",
    "model": "small"  # "small" to help with resource constraints; adjust if needed
}

# Initialize BookNLP with the English language model and parameters
booknlp = BookNLP("en", model_params)

# Process the book; BookNLP will write its outputs to output_dir_bnlp
booknlp.process(local_input_file, output_dir_bnlp, book_id)
print("BookNLP processing complete.")

###########################
# PART 2: Build Coreference Mapping from Entities
###########################
# File paths for BookNLP outputs
entities_file = os.path.join(output_dir_bnlp, f"{book_id}.entities")
quotes_file   = os.path.join(output_dir_bnlp, f"{book_id}.quotes")

# Expected columns: COREF, start_token, end_token, prop, cat, text
person_entities = pd.read_csv(entities_file, sep="\t")

# Filter for person entities (cat == "PER")
person_entities = person_entities[person_entities["cat"] == "PER"]
person_entities = person_entities.sort_values(by=["start_token"])

# Build a mapping: For each unique COREF, collect all mentions.
coref_mentions = defaultdict(list)
for _, row in person_entities.iterrows():
    entity_id = str(row["COREF"])  # Unique ID as string
    mention_text = row["text"]
    coref_mentions[entity_id].append(mention_text)

# Now, build a refined mapping that picks the best (most frequent proper) name per entity.
# Exclude common pronouns from being chosen.
resolved_map = {}
PRONOUNS = {"i", "he", "his", "she", "her", "they", "their", "you", "your", "we", "us", "them", "my", "ourselves"}
for entity_id, mentions in coref_mentions.items():
    # Convert all mentions to strings and filter out pronouns (by comparing lower-case)
    proper_names = [m for m in mentions if isinstance(m, str) and m.istitle() and m.lower() not in PRONOUNS]
    if proper_names:
        resolved_map[entity_id] = max(set(proper_names), key=proper_names.count)
    else:
        non_pronouns = [m for m in mentions if isinstance(m, str) and m.lower() not in PRONOUNS]
        if non_pronouns:
            resolved_map[entity_id] = max(set(non_pronouns), key=non_pronouns.count)
        else:
            resolved_map[entity_id] = "Unknown"

print("Final Coreference Mapping:")
print(resolved_map)

###########################
# PART 3: Process Quotes and Build Output Files
###########################
# Load the quotes file.
# Assumed header columns include: "quote", "char_id", "quote_start", "quote_end"
quotes_df = pd.read_csv(quotes_file, sep="\t", header=0, on_bad_lines='warn')

# Ensure char_id is a string
quotes_df["char_id"] = quotes_df["char_id"].astype(str)

# Map char_id to resolved character names using our refined mapping.
quotes_df["Resolved Speaker"] = quotes_df["char_id"].map(resolved_map)
quotes_df["Resolved Speaker"] = quotes_df["Resolved Speaker"].fillna("Unknown")

# ----------------------
# File 1: Create Character Dialogue File
# ----------------------
character_quotes = {}
for _, row in quotes_df.iterrows():
    speaker = row["Resolved Speaker"]
    quote = row["quote"]
    if speaker not in character_quotes:
        character_quotes[speaker] = []
    character_quotes[speaker].append(f'"{quote}"')

character_dialogue_file = os.path.join(output_dir, f"{book_id}-character-dialogue.txt")
with open(character_dialogue_file, "w", encoding="utf-8") as f:
    for character, quotes in character_quotes.items():
        f.write(f"{character}: {' '.join(quotes)}\n")
print("Character dialogue file created.")

# ----------------------
# File 2: Create Annotated Text File
# ----------------------
with open(local_input_file, "r", encoding="utf-8") as f:
    text = f.read()

# Use regex to find quotes in the text (straight or smart quotes)
pattern = r'(["“][^"”]+["”])'

# We assume the quotes appear in the text in the same order as in the quotes file.
resolved_speakers = quotes_df["Resolved Speaker"].tolist()
speaker_iter = iter(resolved_speakers)

def replacer(match):
    try:
        speaker = next(speaker_iter)
    except StopIteration:
        speaker = "Unknown"
    matched_quote = match.group(0)
    return f'<google:style name="{speaker}"> {matched_quote} </google:style>' #Text to change to update tags

annotated_text = re.sub(pattern, replacer, text, count=0)
audio_text_file = os.path.join(output_dir, f"{book_id}-book-audio-text.txt")
with open(audio_text_file, "w", encoding="utf-8") as f:
    f.write(annotated_text)
print("Annotated text file created.")

###########################
# PART 4: Upload Final Output Files to S3
###########################
# Define S3 keys/prefixes for final outputs (adjust as needed)
s3_output_prefix = f"{book_id}/"
upload_to_s3(character_dialogue_file, S3_OUTPUT_BUCKET, os.path.join(s3_output_prefix, os.path.basename(character_dialogue_file)))
upload_to_s3(audio_text_file, S3_OUTPUT_BUCKET, os.path.join(s3_output_prefix, os.path.basename(audio_text_file)))

print("Final output files uploaded to S3.")

###########################
# (Optional) Cleanup: Remove temporary BookNLP output files if desired.
###########################
for file in os.listdir(output_dir_bnlp):
    file_path = os.path.join(output_dir_bnlp, file)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Failed to delete {file_path}. Reason: {e}")

print("Process completed successfully!")
