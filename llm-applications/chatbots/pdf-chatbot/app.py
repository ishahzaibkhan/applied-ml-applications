from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List
from langchain.agents import create_agent
import streamlit as st
import time
import pymupdf
import re

# load env
load_dotenv()


# Text Pipeline (Opening, Extracting, Sectionwise chunking into dictionary)
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
    end = text.find(filtered_matches[i + 1]) if i + \
        1 < len(filtered_matches) else len(text)

    section_name = re.sub(r'\s+', ' ', filtered_matches[i]).strip()

    section_content = re.sub(r'\s+', ' ', text[start:end]).strip()
    section_content = section_content.replace(section_name, '', 1).strip()

    sections[section_name] = section_content

# # prints key and values of the extracted text with number of character per section
# for key, value in sections.items():
#     print(f"Section: {key}\n")
#     print(f"Content: {len(value)} characters\n")

# print(len(sections))
# print(sections)

# Pydantic class


class Section(BaseModel):
    summary: str = Field(
        ..., description="A concise summary of the main ideas presented in the text.")
    key_points: List[str] = Field(
        ..., description="A list of the key points or takeaways from the text.")

# API Call


llama_instant = "llama-3.1-8b-instant"
llama_versatile = "llama-3.3-70b-versatile"
gpt_oss = "openai/gpt-oss-120b"
response_dict = {}


model = ChatGroq(model=gpt_oss)
agent = create_agent(model=model, response_format=Section)

for key, value in sections.items():
    response = agent.invoke({"messages": [{"role": "system", "content": "You are a helpful assistant that summarizes research articles and gives key points."}, {
                            "role": "user", "content": value}]})
    response_dict[key] = response
    print(f"Section: {key}\n")
    print(response["structured_response"])
    time.sleep(15)  # Add a delay to avoid overwhelming the API

# message = "iran’s Foreign Minister Abbas Araghchi publicly thanked Pakistan’s Prime Minister Shehbaz Sharif and Field Marshal Asim Munir for their “tireless efforts to end the war in the region,” praising Islamabad’s diplomatic push that helped secure a temporary halt to hostili*ties between the United States and Ir@n. Araghchi made the remarks on behalf of Ir@n’s Supreme National Security Council, highlighting Pakistan’s mediation in urging negotiations and responding to calls from both Washington and Tehran as part of the ce@sefire framework. The acknowledgement underscores Pakistan’s growing influence in global diplomacy."

# class Section(BaseModel):
#     summary: str = Field(..., description="A concise summary of the main ideas presented in the text.")
#     key_points: List[str] = Field(..., description="A list of the key points or takeaways from the text.")

# str_model = model.with_structured_output(Section)
# response = str_model.invoke(message)
# print(response.key_points)

# # Streamlit App
# st.title("Scholar Lens")
# st.write("This app breaks down a research article into sections and summarizes each section using an LLM.")
# st.file_uploader("Upload a PDF Research Article", type=["pdf"])
# st.button("Summarize Article Sections")

# menu = ["Home", "Summarized Sections", "All Sections", "Chat with Scholar Lens"]
# with st.sidebar:
#     st.write("Menu")
#     st.radio("Navigate", menu)
