# Research Article Reader
# Take the pdf research article as input.
# Research about different sections in a research article, how each section is contributing to the overall article.
# Extract the sections from the pdf research article using ParsedOutput.
# Extract the summary and key points from each section.
# The language should be easy, concise, yet detailed enough to understand the research article.
# The goal is to understand the research article at least upto 80%.
# The format should be upload pdf and display the output in a well structured manner.
# No QnA format.

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
