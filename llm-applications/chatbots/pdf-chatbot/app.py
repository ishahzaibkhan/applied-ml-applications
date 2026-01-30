import pymupdf
import re

doc = pymupdf.open("./article.pdf")

text = ""
filtered_matches = ["abstract\n"]
counter = 1

for page in doc:
    text += page.get_text().lower()

pattern = re.compile(r'\d\.\n(?:\w+(?:[-\s]\w+){0,4})\n')

matches = pattern.findall(text)

for match in matches:
    if match.startswith(f"{counter}.\n"):
        filtered_matches.append(match)
        counter += 1

sections = {}
for i in range(len(filtered_matches)):
    start = text.find(filtered_matches[i])
    end = text.find(filtered_matches[i + 1]) if i + 1 < len(filtered_matches) else len(text)
    
    # Clean key and value
    section_name = re.sub(r'\s+', ' ', filtered_matches[i]).strip()

    section_content = re.sub(r'\s+', ' ', text[start:end]).strip()
    section_content = section_content.replace(section_name, '', 1).strip()

    sections[section_name] = section_content

for key, value in sections.items():
    print(f"Section: {key}\n")
    print(f"Content: {len(value)} characters\n")

print(len(sections))
print(sections)