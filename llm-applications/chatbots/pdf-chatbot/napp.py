import streamlit as st
import time
import pymupdf
import re
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ScholarLens",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root variables */
:root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #22263a;
    --border: #2e3352;
    --accent: #6c8eff;
    --accent2: #a78bfa;
    --text: #e8eaf6;
    --muted: #8891b8;
    --success: #34d399;
    --warning: #fbbf24;
}

/* Global overrides */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Main content area */
.main .block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 960px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
    padding: 0.5rem 0 0.25rem;
}

/* Radio nav in sidebar */
[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--muted) !important;
    padding: 0.4rem 0.2rem;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
    font-size: 0.92rem;
    text-transform: none;
    letter-spacing: normal;
    font-weight: 400;
}

/* Headers */
h1 { font-family: 'DM Serif Display', serif !important; font-size: 2.4rem !important; font-weight: 400 !important; letter-spacing: -0.02em; color: var(--text) !important; }
h2 { font-family: 'DM Serif Display', serif !important; font-size: 1.6rem !important; font-weight: 400 !important; color: var(--text) !important; }
h3 { font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent) !important; }

/* Cards */
.sl-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.2rem;
}
.sl-card-accent {
    background: linear-gradient(135deg, #1a1d27 0%, #1e2035 100%);
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.2rem;
}

/* Section header pill */
.sl-pill {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 0.2rem 0.9rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    margin-bottom: 0.75rem;
}

/* Keypoint list */
.sl-keypoint {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 0.6rem;
    align-items: flex-start;
    font-size: 0.9rem;
    color: var(--text);
    line-height: 1.5;
}
.sl-keypoint-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    margin-top: 0.45rem;
    flex-shrink: 0;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.5rem !important;
    letter-spacing: 0.02em;
    transition: opacity 0.15s ease;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:disabled { opacity: 0.4 !important; }

/* Text input */
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(108,142,255,0.15) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin-bottom: 0.6rem !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Success / info / warning */
.stSuccess { background: rgba(52,211,153,0.1) !important; border: 1px solid var(--success) !important; border-radius: 8px !important; }
.stInfo    { background: rgba(108,142,255,0.1) !important; border: 1px solid var(--accent) !important; border-radius: 8px !important; }
.stWarning { background: rgba(251,191,36,0.1) !important; border: 1px solid var(--warning) !important; border-radius: 8px !important; }

/* Expander */
details {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin-bottom: 0.75rem !important;
}
details summary {
    color: var(--text) !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.25rem;
}

/* Progress bar */
.stProgress > div > div { background: var(--accent) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "groq_key_set": False,
    "groq_api_key": "",
    "paper_text": "",
    "sections": {},
    "summaries": {},      # {section_name: {summary, key_points}}
    "chat_history": [],
    "paper_uploaded": False,
    "paper_name": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_sections(pdf_bytes: bytes) -> tuple[str, dict]:
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text().lower()

    filtered_matches = ["abstract\n"]
    counter = 1
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
        section_name = re.sub(r'\s+', ' ', filtered_matches[i]).strip()
        section_content = re.sub(r'\s+', ' ', text[start:end]).strip()
        section_content = section_content.replace(section_name, '', 1).strip()
        sections[section_name] = section_content

    return text, sections


class Section(BaseModel):
    summary: str = Field(..., description="A concise summary of the main ideas.")
    key_points: List[str] = Field(..., description="Key points or takeaways.")


def summarize_sections(sections: dict, api_key: str) -> dict:
    from langchain.agents import create_react_agent
    # Use structured output directly via with_structured_output
    model = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)
    structured_model = model.with_structured_output(Section)

    results = {}
    for key, value in sections.items():
        messages = [
            {"role": "system", "content": "You are a research assistant. Summarize the section and list key points."},
            {"role": "user", "content": value[:4000]},  # cap tokens
        ]
        try:
            response = structured_model.invoke(messages)
            results[key] = {"summary": response.summary, "key_points": response.key_points}
        except Exception as e:
            results[key] = {"summary": f"Error: {e}", "key_points": []}
        time.sleep(1)
    return results


def rag_answer(question: str, context: str, api_key: str) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)
    prompt = f"""You are a helpful research assistant. Answer the user's question based ONLY on the provided paper content.

Paper content (truncated):
{context[:6000]}

Question: {question}

Answer concisely and cite the relevant section if possible."""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {e}"


def discover_papers(query: str, api_key: str) -> str:
    model = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
    prompt = f"""You are a research discovery assistant. Based on the topic or query below, suggest 5 relevant research papers.

For each paper provide:
- Title
- Authors (plausible)
- Year
- Why it's relevant (1–2 sentences)

Query / Topic: {query}

Format each paper as a numbered list."""
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {e}"

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔬 ScholarLens")
    st.markdown("---")

    # API key section
    st.markdown("**API KEY**")
    with st.expander("🔑 Groq API Key", expanded=not st.session_state.groq_key_set):
        key_input = st.text_input(
            "Enter your Groq API Key",
            type="password",
            value=st.session_state.groq_api_key,
            placeholder="gsk_...",
            label_visibility="collapsed",
        )
        if st.button("Save Key", key="save_key"):
            if key_input.startswith("gsk_") or len(key_input) > 20:
                st.session_state.groq_api_key = key_input
                st.session_state.groq_key_set = True
                st.success("Key saved ✓")
            else:
                st.error("Invalid key format")

    if st.session_state.groq_key_set:
        st.success("✓ API key active")

    st.markdown("---")
    st.markdown("**NAVIGATION**")

    page = st.radio(
        "nav",
        options=["🏠  Home", "📄  Full Paper", "📑  Section Summaries", "💬  Chat with Paper", "🔍  Discover Papers"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.session_state.paper_uploaded:
        st.markdown(f'<div class="sl-pill">📎 {st.session_state.paper_name[:28]}...</div>', unsafe_allow_html=True)
        sections_count = len(st.session_state.sections)
        st.markdown(f"<span style='color:var(--muted);font-size:0.8rem'>{sections_count} sections detected</span>", unsafe_allow_html=True)

# ── Gate: require API key ─────────────────────────────────────────────────────
if not st.session_state.groq_key_set:
    st.markdown('<div class="sl-card-accent">', unsafe_allow_html=True)
    st.markdown("## Welcome to ScholarLens 🔬")
    st.markdown("An AI-powered research paper analysis tool. To get started, enter your **Groq API key** in the sidebar.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.info("👈 Open the sidebar and enter your Groq API Key to begin.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if page.startswith("🏠"):
    st.markdown("# ScholarLens")
    st.markdown('<p style="color:var(--muted);font-size:1.05rem;margin-top:-0.5rem">AI-powered research paper analysis</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        st.markdown("### What ScholarLens does")
        features = [
            ("📄", "Full Paper Viewer", "Extracts and displays all text from your PDF"),
            ("📑", "Section Summaries", "AI-generated summary + key points per section"),
            ("💬", "RAG-based Chat", "Ask questions, get answers grounded in the paper"),
            ("🔍", "Discover Papers", "Find related research by topic or gap"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="display:flex;gap:0.9rem;margin-bottom:0.9rem;align-items:flex-start">
                <span style="font-size:1.3rem">{icon}</span>
                <div>
                    <div style="font-weight:600;font-size:0.9rem;color:var(--text)">{title}</div>
                    <div style="font-size:0.82rem;color:var(--muted)">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        st.markdown("### Upload Paper")
        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            st.markdown(f'<div class="sl-pill">📎 {uploaded.name}</div>', unsafe_allow_html=True)
            st.markdown(f"<span style='color:var(--muted);font-size:0.8rem'>{uploaded.size / 1024:.1f} KB</span>", unsafe_allow_html=True)

            if st.button("⚡ Process Paper"):
                with st.spinner("Extracting text and detecting sections..."):
                    pdf_bytes = uploaded.read()
                    text, sections = extract_sections(pdf_bytes)
                    st.session_state.paper_text = text
                    st.session_state.sections = sections
                    st.session_state.paper_uploaded = True
                    st.session_state.paper_name = uploaded.name
                    st.session_state.summaries = {}  # reset on new upload
                st.success(f"✓ Extracted {len(sections)} sections")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.paper_uploaded:
        st.markdown("---")
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        st.markdown("### Paper Overview")
        sec_names = list(st.session_state.sections.keys())
        cols = st.columns(min(len(sec_names), 4))
        for i, name in enumerate(sec_names):
            with cols[i % 4]:
                word_count = len(st.session_state.sections[name].split())
                st.markdown(f"""
                <div style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:0.75rem;margin-bottom:0.5rem">
                    <div style="font-size:0.75rem;color:var(--accent);font-weight:600;text-transform:uppercase;letter-spacing:0.08em">{name[:30]}</div>
                    <div style="font-size:0.8rem;color:var(--muted);margin-top:0.3rem">~{word_count} words</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FULL PAPER
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("📄"):
    st.markdown("# Full Paper")
    st.markdown("---")

    if not st.session_state.paper_uploaded:
        st.info("👈 Upload a paper on the Home page first.")
    else:
        st.markdown(f'<div class="sl-pill">📎 {st.session_state.paper_name}</div>', unsafe_allow_html=True)

        search_term = st.text_input("🔎 Search in paper", placeholder="Type to search...", label_visibility="visible")

        for section_name, content in st.session_state.sections.items():
            highlight = bool(search_term and search_term.lower() in content.lower())
            border_color = "var(--accent)" if highlight else "var(--border)"
            with st.expander(f"{'🔆 ' if highlight else ''}{section_name.title()}", expanded=highlight):
                display_content = content
                if search_term and search_term.lower() in content.lower():
                    # Show snippet around match
                    idx = content.lower().find(search_term.lower())
                    start = max(0, idx - 200)
                    end = min(len(content), idx + 400)
                    snippet = f"...{content[start:end]}..."
                    st.markdown(f"<span style='color:var(--warning);font-size:0.8rem'>Match found</span>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size:0.88rem;line-height:1.7;color:var(--muted)'>{snippet}</p>", unsafe_allow_html=True)
                    with st.expander("Show full section"):
                        st.markdown(f"<p style='font-size:0.88rem;line-height:1.7;color:var(--muted)'>{content}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='font-size:0.88rem;line-height:1.7;color:var(--muted)'>{content[:3000]}{'...' if len(content) > 3000 else ''}</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUMMARIZED SECTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("📑"):
    st.markdown("# Section Summaries")
    st.markdown("---")

    if not st.session_state.paper_uploaded:
        st.info("👈 Upload a paper on the Home page first.")
    else:
        if not st.session_state.summaries:
            st.markdown('<div class="sl-card">', unsafe_allow_html=True)
            st.markdown(f"**{len(st.session_state.sections)} sections** detected in paper. Click below to generate AI summaries.")
            st.markdown(f"<span style='color:var(--muted);font-size:0.82rem'>Model: llama-3.1-8b-instant · Est. time: ~{len(st.session_state.sections) * 3}s</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("✨ Generate All Summaries"):
                progress = st.progress(0, text="Summarizing sections...")
                sections = st.session_state.sections
                total = len(sections)
                results = {}

                model = ChatGroq(model="llama-3.1-8b-instant", api_key=st.session_state.groq_api_key)
                structured_model = model.with_structured_output(Section)

                for i, (key, value) in enumerate(sections.items()):
                    progress.progress((i + 1) / total, text=f"Summarizing: {key[:40]}...")
                    messages = [
                        {"role": "system", "content": "You are a research assistant. Summarize the section and list key points."},
                        {"role": "user", "content": value[:4000]},
                    ]
                    try:
                        response = structured_model.invoke(messages)
                        results[key] = {"summary": response.summary, "key_points": response.key_points}
                    except Exception as e:
                        results[key] = {"summary": f"Error: {e}", "key_points": []}
                    time.sleep(1)

                st.session_state.summaries = results
                progress.empty()
                st.success("✓ All sections summarized!")
                st.rerun()
        else:
            st.markdown(f'<span style="color:var(--success);font-size:0.85rem">✓ {len(st.session_state.summaries)} sections summarized</span>', unsafe_allow_html=True)

            if st.button("↺ Re-generate"):
                st.session_state.summaries = {}
                st.rerun()

            st.markdown("")

            for section_name, data in st.session_state.summaries.items():
                st.markdown(f'<div class="sl-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="sl-pill">{section_name.title()}</div>', unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.9rem;line-height:1.65;color:var(--text);margin-bottom:1rem'>{data['summary']}</p>", unsafe_allow_html=True)

                if data["key_points"]:
                    st.markdown("<div style='font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--accent);margin-bottom:0.5rem'>Key Points</div>", unsafe_allow_html=True)
                    for kp in data["key_points"]:
                        st.markdown(f"""<div class="sl-keypoint">
                            <div class="sl-keypoint-dot"></div>
                            <span>{kp}</span>
                        </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("💬"):
    st.markdown("# Chat with Paper")
    st.markdown("<p style='color:var(--muted);margin-top:-0.5rem;font-size:0.9rem'>Ask anything about the uploaded paper</p>", unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.paper_uploaded:
        st.info("👈 Upload a paper on the Home page first.")
    else:
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
        question = st.chat_input("Ask a question about the paper...")

        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = rag_answer(question, st.session_state.paper_text, st.session_state.groq_api_key)
                st.markdown(answer)

            st.session_state.chat_history.append({"role": "assistant", "content": answer})

        if st.session_state.chat_history:
            if st.button("🗑 Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DISCOVER PAPERS
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("🔍"):
    st.markdown("# Discover Papers")
    st.markdown("<p style='color:var(--muted);margin-top:-0.5rem;font-size:0.9rem'>Find related research articles using AI</p>", unsafe_allow_html=True)
    st.markdown("---")

    col_a, col_b = st.columns([2, 1])

    with col_a:
        search_mode = st.selectbox(
            "Discovery mode",
            ["Similar Papers", "Papers on Limitations", "Papers on Methodology", "Papers Citing This Work", "Custom Query"],
        )

    with col_b:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        auto_topic = ""
        if st.session_state.paper_uploaded and search_mode != "Custom Query":
            # Derive a short topic from paper text
            auto_topic = st.session_state.paper_text[:300]

    # Build query
    if search_mode == "Similar Papers":
        query_hint = f"Find research papers similar to this topic: {auto_topic}" if auto_topic else "similar research papers in NLP and machine learning"
    elif search_mode == "Papers on Limitations":
        query_hint = f"Find research papers that address limitations of: {auto_topic}" if auto_topic else "papers addressing limitations in AI research"
    elif search_mode == "Papers on Methodology":
        query_hint = f"Find papers using similar methodology to: {auto_topic}" if auto_topic else "papers on research methodology"
    elif search_mode == "Papers Citing This Work":
        query_hint = f"Find research papers that would cite work on: {auto_topic}" if auto_topic else "foundational papers in deep learning"
    else:
        query_hint = ""

    custom_query = st.text_input(
        "Search topic or describe what you're looking for",
        value=query_hint,
        placeholder="e.g. transformer models for low-resource languages",
    )

    if st.button("🔍 Discover"):
        if custom_query.strip():
            with st.spinner("Discovering related papers..."):
                result = discover_papers(custom_query, st.session_state.groq_api_key)

            st.markdown("---")
            st.markdown("### Recommended Papers")
            st.markdown('<div class="sl-card">', unsafe_allow_html=True)
            # Parse and display nicely
            lines = result.strip().split("\n")
            for line in lines:
                if line.strip():
                    if line.strip()[0].isdigit() and "." in line[:3]:
                        st.markdown(f"<div style='font-weight:600;color:var(--text);margin-top:1rem;font-size:0.92rem'>{line}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='color:var(--muted);font-size:0.87rem;margin-left:1rem'>{line}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter a search query.")