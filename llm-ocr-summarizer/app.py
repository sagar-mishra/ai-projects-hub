import streamlit as st
import ollama
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="LLM-based OCR with Ollama", layout="centered")
st.title("🧠 LLM OCR (Text Extraction + Summarization)")
st.markdown("""
Upload an image (receipt, document, etc.) and let a local LLM extract structured text using image understanding.
""")

# Persist uploaded file in session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

uploaded = st.file_uploader("📷 Upload an image", type=["png", "jpg", "jpeg"])
if uploaded:
    st.session_state.uploaded_file = uploaded

# Mode Selection
mode = st.selectbox("Choose Mode", ["OCR", "OCR + Summarize"])

# Available vision models (add or change based on your Ollama setup)
available_models = ["llava", "llama3.2-vision", "gemma3:4b"]
selected_model = st.selectbox("🤖 Choose a Vision-Enabled LLM", available_models)


# Show uploaded image
if st.session_state.uploaded_file:
    st.image(st.session_state.uploaded_file, caption="Uploaded Image", use_container_width=True)

# Trigger analysis
if st.session_state.uploaded_file and st.button("🔍 Process Image"):

    with st.spinner(f"🔎 Processing with {selected_model}..."):
        try:
            image_bytes = st.session_state.uploaded_file.getvalue()

            if mode == "OCR":
                # Simple OCR task
                    prompt = (
                    "This is an OCR task. Please extract and transcribe all readable text from the image. "
                    "Preserve the layout and do not summarize. Return only the extracted text."
                    )
            else:
                 # OCR + Summarize
                 prompt = (
                    "Analyze the image for text content. Extract all readable text and summarize it in a clean, "
                    "structured Markdown format using lists, headings, or code blocks where needed. Focus on clarity."
                )
            
            response = ollama.chat(
                model=selected_model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_bytes]
                }]
            )


          
            st.subheader(f"📄 {mode} Output : ")
            st.markdown(response['message']['content'])

        except Exception as e:
            st.error(f"❌ Failed to process the image. Error: {e}")
else:
    st.info("Upload an image and click the button to begin.")
