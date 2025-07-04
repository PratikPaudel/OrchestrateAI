import sys
import os
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.enums import XPos, YPos # Import necessary enums


# --- Environment and Path Setup ---
# Load environment variables from .env file at the project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
# Add the project root to the Python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.supervisor import SupervisorAgent

# --- Page Configuration and Styling ---
st.set_page_config(page_title="OrchestrateAI", page_icon="🤖", layout="centered")

# --- Enhanced CSS for improved UI ---
st.markdown("""
<style>
    /* Main app background with animated gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #1e293b 75%, #0f172a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: #e2e8f0;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header container */
    .header-container {
        text-align: center;
        padding: 2rem 0 1rem 0; /* Adjusted padding */
    }
    
    /* Enhanced title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 20px rgba(59, 130, 246, 0.6), 0 0 40px rgba(59, 130, 246, 0.4);
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientText 3s ease infinite;
    }
    
    @keyframes gradientText {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.25rem;
        color: #cbd5e1;
        margin-bottom: 1.5rem; /* Adjusted margin */
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    /* Search container */
    .search-container {
        max-width: 700px;
        margin: 2rem auto 2rem auto; /* Adjusted margin */
        padding: 0 1rem;
    }
    
    /* Enhanced chat input styling */
    .stChatInput {
        background: rgba(51, 65, 85, 0.8);
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-radius: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stChatInput:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2), 0 8px 32px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    .stChatInput input {
        color: #e2e8f0 !important;
        font-size: 1.1rem;
        padding: 1rem 1.5rem;
        background: transparent !important;
        border: none !important;
    }
    
    .stChatInput input::placeholder {
        color: #94a3b8 !important;
        font-style: italic;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(51, 65, 85, 0.6);
        border-radius: 16px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        border: none;
        border-radius: 12px;
        color: white;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        background: linear-gradient(45deg, #2563eb, #7c3aed);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #10b981, #059669);
        border: none;
        border-radius: 12px;
        color: white;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
        background: linear-gradient(45deg, #059669, #047857);
    }
    
    /* JSON display styling */
    .stJson {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: rgba(51, 65, 85, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        color: #e2e8f0;
        font-family: 'Courier New', monospace;
    }
    
    /* Info box styling */
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Spinner styling */
    .stSpinner > div > div {
        border-top-color: #3b82f6;
        border-right-color: #8b5cf6;
    }
    
    /* Balloons container */
    .stBalloons {
        pointer-events: none;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .subtitle {
            font-size: 1.1rem;
            padding: 0 1rem;
        }
        
        .search-container {
            padding: 0 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def create_pdf_report(report_text):
    """Creates a PDF file from a Markdown string using a Unicode font."""
    pdf = FPDF()
    
    # Add fonts without the deprecated 'uni' parameter
    try:
        pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf")
        pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf")
        font_family = "DejaVu"
    except RuntimeError as e:
        print(f"Font loading error: {e}. Falling back to Arial.")
        st.warning("Could not load custom font. PDF may have rendering issues.")
        font_family = "Arial"

    pdf.add_page()
    pdf.set_font(font_family, size=12)
    
    # Set margins for better text wrapping
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)

    def wrap_long_text(text, max_width=80):
        """Wrap long lines that might cause rendering issues."""
        if len(text) <= max_width:
            return text
        
        # Split very long words/URLs
        words = text.split()
        wrapped_words = []
        
        for word in words:
            if len(word) > max_width:
                # Break long words into chunks
                chunks = [word[i:i+max_width] for i in range(0, len(word), max_width)]
                wrapped_words.extend(chunks)
            else:
                wrapped_words.append(word)
        
        return ' '.join(wrapped_words)

    lines = report_text.split('\n')
    for line in lines:
        try:
            # Wrap long lines to prevent horizontal overflow
            wrapped_line = wrap_long_text(line)
            
            if line.startswith('# '):
                pdf.set_font(font_family, 'B', 16)
                pdf.multi_cell(0, 10, wrapped_line[2:], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                pdf.set_font(font_family, '', 12)
            elif line.startswith('## '):
                pdf.set_font(font_family, 'B', 14)
                pdf.multi_cell(0, 10, wrapped_line[3:], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font(font_family, '', 12)
            elif line.startswith('### '):
                pdf.set_font(font_family, 'B', 12)
                pdf.multi_cell(0, 8, wrapped_line[4:], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font(font_family, '', 12)
            else:
                # Check for empty lines to avoid adding extra space
                if line.strip():
                    pdf.multi_cell(0, 5, wrapped_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    pdf.ln(5)  # Just add a line break for empty lines
                    
        except Exception as e:
            # If there's still an error with a specific line, skip it and add a note
            print(f"Error processing line: {line[:50]}... Error: {e}")
            pdf.multi_cell(0, 5, "[Content could not be rendered]", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Return the PDF content as bytes (convert bytearray to bytes)
    return bytes(pdf.output(dest='S'))


# --- Agent and State Initialization ---
if 'supervisor' not in st.session_state:
    st.session_state.supervisor = SupervisorAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'step' not in st.session_state:
    st.session_state.step = 'start'


# --- Custom Header ---
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🤖 OrchestrateAI</h1>
    <p class="subtitle">Multi-Agent Research Agency</p>
    <p class="subtitle" style="font-size: 1rem; margin-bottom: 0;">Submit a research query, and our AI agent team will build a comprehensive report. You are the manager, approving each step.</p>
</div>
""", unsafe_allow_html=True)


# --- Display existing messages ---
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)
        # Re-display download buttons if they exist for the final message
        if msg.get("is_final_report"):
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="⬇️ Download as Markdown", data=st.session_state.final_report,
                    file_name="OrchestrateAI_Report.md", mime="text/markdown")
            with col2:
                st.download_button(
                    label="📄 Download as PDF", data=st.session_state.pdf_bytes,
                    file_name="OrchestrateAI_Report.pdf", mime="application/pdf")


# --- State Machine for the workflow ---
if st.session_state.step == 'start':
    # The user is prompted to enter their query in the middle of the screen.
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        if user_query := st.chat_input('🔍 Enter your research topic... (e.g., "Latest trends in AI", "Climate change impacts")'):
            st.session_state.user_query = user_query
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.step = 'research'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Example queries are shown below the main input area.
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; opacity: 0.7;">
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem;">💡 Example queries to get you started:</p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span style="background: rgba(59, 130, 246, 0.1); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">Latest AI developments</span>
                <span style="background: rgba(59, 130, 246, 0.1); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">Renewable energy trends</span>
                <span style="background: rgba(59, 130, 246, 0.1); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">Market analysis 2024</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.step == 'research':
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Researcher is gathering information..."):
            research_results = st.session_state.supervisor.researcher.handle_query(st.session_state.user_query)
            st.session_state.research_results = research_results
        
        st.markdown("### 📊 Research Findings")
        st.markdown("Here are the sources and summaries found by the Researcher. Please review and approve.")
        st.json(research_results)

        if st.button('✅ Approve Research'):
            st.session_state.messages.append({"role": "assistant", "content": "✅ **Research Approved!** The findings have been passed to the Analyst."})
            st.session_state.step = 'analysis'
            st.rerun()

elif st.session_state.step == 'analysis':
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔬 Analyst is processing the data..."):
            analysis_code = f"import pprint\npprint.pprint({st.session_state.research_results})"
            analysis_results = st.session_state.supervisor.analyst.analyze(analysis_code)
            st.session_state.analysis_results = analysis_results

        st.markdown("### 🧮 Analysis Results")
        st.markdown("The Analyst has processed the research data. Please review and approve.")
        st.text_area("Analysis Output", value=analysis_results, height=200, disabled=True)

        if st.button('✅ Approve Analysis'):
            st.session_state.messages.append({"role": "assistant", "content": "✅ **Analysis Approved!** The report is now being drafted."})
            st.session_state.step = 'report'
            st.rerun()

elif st.session_state.step == 'report':
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("✍️ Writer is drafting the final report..."):
            final_report = st.session_state.supervisor.writer.write_report(st.session_state.research_results, st.session_state.analysis_results)
            st.session_state.final_report = final_report
            pdf_bytes = create_pdf_report(final_report)
            st.session_state.pdf_bytes = pdf_bytes

        st.markdown("### 📄 Final Report")
        st.markdown(final_report)
        st.balloons()
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"**📄 Final Report Complete!**\n\n{final_report}",
            "is_final_report": True
        })
        st.session_state.step = 'done'
        st.rerun()

elif st.session_state.step == 'done':
    st.info("🎉 Report generation complete! You can download the report above or start a new research task.")
    if st.button('🆕 Start New Research'):
        # Keep supervisor, clear everything else to start fresh
        supervisor = st.session_state.supervisor
        st.session_state.clear()
        st.session_state.supervisor = supervisor
        st.session_state.step = 'start'
        st.session_state.messages = []
        st.rerun()