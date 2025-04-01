
import spacy
nlp = spacy.load("en_core_web_sm")
print("SpaCy model loaded successfully!")

from booknlp.booknlp import BookNLP

# Define model parameters
model_params = {
    "pipeline": "entity,quote,supersense,event,coref",
    "model": "small"
}

# Initialize BookNLP with the English language model and parameters
booknlp = BookNLP("en", model_params)

# Define input and output paths
input_file = "/yunity/arusty/SoundScribe/text_files/chapter4.txt"
output_dir = "/yunity/arusty/SoundScribe/text_files/book_files"
book_id = "lotl_chapter4"

# Process the book
booknlp.process(input_file, output_dir, book_id)