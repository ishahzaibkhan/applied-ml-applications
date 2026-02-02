from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List
import streamlit as st
import pymupdf
import re

load_dotenv()

message = "by“explaining a prediction”, we mean presenting textual or visual artifacts that provide qualitative understanding of the relationship between the instance’s components (e.g. words in text, patches in an image) and the model’s prediction. we argue that explaining predictions is an important aspect in arxiv:1602.04938v3 [cs.lg] 9 aug 2016 sneeze weight headache no fatigue age flu sneeze headache model data and prediction explainer (lime) explanation no fatigue human makes decision figure 1: explaining individual predictions. a model predicts that a patient has the ﬂu, and lime highlights the symptoms in the patient’s history that led to the prediction. sneeze and headache are portrayed as contributing to the “ﬂu” prediction, while “no fatigue” is evidence against it. with these, a doctor can make an informed decision about whether to trust the model’s prediction. getting humans to trust and use machine learning eﬀectively, if the explanations are faithful and intelligible. the process of explaining individual predictions is illus- trated in figure 1. it is clear that a doctor is much better positioned to make a decision with the help of a model if intelligible explanations are provided. in this case, an ex- planation is a small list of symptoms with relative weights – symptoms that either contribute to the prediction (in green) or are evidence against it (in red). humans usually have prior knowledge about the application domain, which they can use to accept (trust) or reject a prediction if they understand the reasoning behind it. it has been observed, for example, that providing explanations can increase the acceptance of movie recommendations [12] and other automated systems [8]. every machine learning application also requires a certain measure of overall trust in the model. development and evaluation of a classiﬁcation model often consists of collect- ing annotated data, of which a held-out subset is used for automated evaluation. although this is a useful pipeline for many applications, evaluation on validation data may not correspond to performance “in the wild”, as practitioners often overestimate the accuracy of their models [20], and thus trust cannot rely solely on it. looking at examples oﬀers an alternative method to assess truth in the model, especially if the examples are explained. we thus propose explaining several representative individual predictions of a model as a way to provide a global understanding. there are several ways a model or its evaluation can go wrong. data leakage, for example, deﬁned as the uninten- tional leakage of signal into the training (and validation) data that would not appear when deployed [14], potentially increases accuracy. a challenging example cited by kauf- man et al. [14] is one where the patient id was found to be heavily correlated with the target class in the training and validation data. this issue would be incredibly challenging to identify just by observing the predictions and the raw data, but much easier if explanations such as the one in figure 1 are provided, as patient id would be listed as an explanation for predictions. another particularly hard to detect problem is dataset shift [5], where training data is diﬀerent than test data (we give an example in the famous 20 newsgroups dataset later on). the insights given by expla- nations are particularly helpful in identifying what must be done to convert an untrustworthy model into a trustworthy one – for example, removing leaked data or changing the training data to avoid dataset shift. machine learning practitioners often have to select a model from a number of alternatives, requiring them to assess the relative trust between two or more models. in figure figure 2: explaining individual predictions of com- peting classiﬁers trying to determine if a document is about “christianity” or “atheism”. the bar chart represents the importance given to the most rele- vant words, also highlighted in the text. color indi- cates which class the word contributes to (green for “christianity”, magenta for “atheism”). 2, we show how individual prediction explanations can be used to select between models, in conjunction with accuracy. in this case, the algorithm with higher accuracy on the validation set is actually much worse, a fact that is easy to see when explanations are provided (again, due to human prior knowledge), but hard otherwise. further, there is frequently a mismatch between the metrics that we can compute and optimize (e.g. accuracy) and the actual metrics of interest such as user engagement and retention. while we may not be able to measure such metrics, we have knowledge about how certain model behaviors can inﬂuence them. therefore, a practitioner may wish to choose a less accurate model for content recommendation that does not place high importance in features related to “clickbait” articles (which may hurt user retention), even if exploiting such features increases the accuracy of the model in cross validation. we note that explanations are particularly useful in these (and other) scenarios if a method can produce them for any model, so that a variety of models can be compared. desired characteristics for explainers we now outline a number of desired characteristics from explanation methods. an essential criterion for explanations is that they must be interpretable, i.e., provide qualitative understanding between the input variables and the response. we note that interpretability must take into account the user’s limitations. thus, a linear model [24], a gradient vector [2] or an additive model [6] may or may not be interpretable. for example, if hundreds or thousands of features signiﬁcantly contribute to a prediction, it is not reasonable to expect any user to comprehend why the prediction was made, even if individual weights can be inspected. this requirement further implies that explanations should be easy to understand, which is not necessarily true of the features used by the model, and thus the “input variables” in the explanations may need to be diﬀerent than the features. finally, we note that the notion of interpretability also depends on the target audience. machine learning practitioners may be able to interpret small bayesian networks, but laymen may be more comfortable with a small number of weighted features as an explanation. another essential criterion is local ﬁdelity. although it is often impossible for an explanation to be completely faithful unless it is the complete description of the model itself, for an explanation to be meaningful it must at least be locally faithful, i.e. it must correspond to how the model behaves in the vicinity of the instance being predicted. we note that local ﬁdelity does not imply global ﬁdelity: features that are globally important may not be important in the local context, and vice versa. while global ﬁdelity would imply local ﬁdelity, identifying globally faithful explanations that are interpretable remains a challenge for complex models. while there are models that are inherently interpretable [6, 17, 26, 27], an explainer should be able to explain any model, and thus be model-agnostic (i.e. treat the original model as a black box). apart from the fact that many state-of- the-art classiﬁers are not currently interpretable, this also provides ﬂexibility to explain future classiﬁers. in addition to explaining predictions, providing a global perspective is important to ascertain trust in the model. as mentioned before, accuracy may often not be a suitable metric to evaluate the model, and thus we want to explain the model. building upon the explanations for individual predictions, we select a few explanations to present to the user, such that they are representative of the model."
model = ChatGroq(model="llama-3.3-70b-versatile")

class Section(BaseModel):
    summary: str = Field(..., description="A concise summary of the main ideas presented in the text.")
    key_points: List[str] = Field(..., description="A list of the key points or takeaways from the text.")

str_model = model.with_structured_output(Section)
response = str_model.invoke(message)
print(response.key_points)

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


st.title("Research Article Reader")
st.write("This app breaks down a research article into sections and summarizes each section using an LLM.")
st.file_uploader("Upload a PDF Research Article", type=["pdf"])
st.button("Summarize Article Sections")

# for key, value in sections.items():
#     print(f"Section: {key}\n")
#     print(f"Content: {len(value)} characters\n")

# print(len(sections))
# print(sections)