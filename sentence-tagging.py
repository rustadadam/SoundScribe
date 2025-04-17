from sagemaker.s3 import S3Uploader, S3Downloader
from pathlib import Path

import json
import re


if __name__ == '__main__':
    book_path = Path('book-text-info/alice-in-wonderland')

    book_text = book_path.joinpath(f'{book_path.name}-book-audio-text.txt')
    if 'alice' in book_path.name or 'frank' in book_path.name:
        with open(book_text) as f:
            lines = f.read()
    else:
        with open(book_text) as f:
            lines = f.readlines()

    if isinstance(lines, str):
        new_lines = []

        old_lines = lines.split('\n')
        start = True
        one_liner = ''
        for line in old_lines:
            # group by paragraphs
            if len(line.strip()) == 0:
                new_lines.append(one_liner)
                one_liner = ''
                continue
            one_liner += line.strip() + ' '
        lines = new_lines

    voice_bucket = 's3://sound-scribe-acessories/working-voices.json'
    downloader = S3Downloader()
    downloader.download(voice_bucket, '.')

    quote_path = book_path.joinpath(f'{book_path.name}-person-quotes.json')
    with open(quote_path) as f:
        person_quotes = json.load(f)

    with open('working-voices.json') as f:
        voices = json.load(f)

    narrator = "en-US-Polyglot-1"

    voices = voices['voices']
    voices.remove(narrator)

    voice_name = {name: voices[i % len(voices)] for i, name in enumerate(person_quotes)}

    replace_counts = {name: 0 for name, quotes in person_quotes.items()}
    new_lines = ['<speak>\n']
    for line in lines:
        new_line = ''
        pattern = r"</[a-zA-Z ’]+>"
        # Find all the name tags
        res = re.findall(pattern, line)
        if len(res) == 0:
            new_lines.append(line)
            continue

        pattern = r"“[’a-zA-Z \[\],?!.\—:\(\)_”]*"
        words = re.findall(pattern, line)
        # print(line)
        # print(words)
        start = 0
        for r, w in zip(res, words):
            # Get the index of the start of </name>
            r_idx = line.index(r)
            # Add all characters up until that point
            new_line += line[start:r_idx]
            # Update start to point to the end of r
            start += len(r) + r_idx

            # Get the index of the quote
            w_idx = line.index(w)
            # Add all characters from the end of the </name> to the quote
            new_line += line[start:w_idx]

            # Extract the name from the </name>
            name = r[2:-1]
            # Get the index from the quote gathering dictionary
            idx = replace_counts[name]
            # Get a random voice
            tts_voice = voice_name[name]
            try:
                # Surround the quote in the proper voice tags
                voice_quote = f"<voice name=\"{tts_voice}\">{person_quotes[name][idx]}</voice>"
                # Substitute the quote with the tagged quote
                s = re.sub(pattern, w, voice_quote)
                # Update the new_line to include this information
                new_line += s
            except Exception as e:
                print(e)

            # Update start to point at the end of the quote
            start += len(w) + w_idx
            # Update replace counts to make sure we get all the quotes
            replace_counts[name] += 1
        # Add the rest of the line to the new line
        new_line += line[start:]
        new_line += '\n'
        new_lines.append(new_line)
    new_lines.append('</speak>')

    tagged_path = book_path.joinpath(f'{book_path.name}-book-audio-text-tagged.txt')
    with open(tagged_path, 'w') as f:
        f.writelines(new_lines)

    quote_bucket = f's3://book-text-info/{book_path.name}'
    uploader = S3Uploader()
    uploader.upload(tagged_path, quote_bucket)