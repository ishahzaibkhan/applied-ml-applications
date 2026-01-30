import pymupdf
import re

# Load the PDF document
doc = pymupdf.open("./article.pdf")

text = ""
filtered_matches = []
counter = 1

for page in doc:
    text += page.get_text().lower()

pattern = re.compile(r'\d\.\n(?:\w+(?:[-\s]\w+){0,4})\n')

matches = pattern.findall(text)

for match in matches:
    if match.startswith(f"{counter}.\n"):
        filtered_matches.append(match)
        counter += 1

for match in filtered_matches:
    print(match)
