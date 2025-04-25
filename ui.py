# File: ui.py

import gradio as gr
import os
import traceback
import tempfile
import piper    # For Text-to-Speech
import wave     # For writing WAV file correctly

# Core components
from app.core.embedding_model import EmbeddingModel
from app.core.faiss_wrapper import FaissIndex
from app.core.llm import generate_answer

# Utils and Agents
from app.utils.chunker import split_text
from app.utils.file_reader import extract_text_from_raw # Import the updated extractor
from app.agent.policy_reviewer import analyze_policies

# --- Initialization ---
tts_voice = None # Variable to hold the loaded voice
embedder = None
faiss_index = None
try:
    # Initialize Embedder and FAISS
    embedder = EmbeddingModel(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
    faiss_index = FaissIndex(dim=384)
    print("Embedder and FAISS initialized successfully.")

    # ---- Initialize Piper TTS ----
    # Define paths based on your project structure
    model_path = "app/models/tts/en_US-danny-low.onnx"
    config_path = "app/models/tts/en_US-danny-low.onnx.json"

    if os.path.exists(model_path) and os.path.exists(config_path):
        print(f"Loading Piper TTS voice from: {model_path}")
        try:
            from piper.voice import PiperVoice # Ensure correct import if needed
            tts_voice = PiperVoice.load(model_path, config_path=config_path)
            print("Piper TTS voice (en_US-danny-low) loaded successfully.")
        except Exception as piper_e:
             print(f"Could not initialize Piper TTS voice with PiperVoice.load. Error: {piper_e}")
             print("Please check piper-tts documentation or installation.")
             tts_voice = None # Ensure it's None if loading failed
    else:
        print(f"Warning: Piper TTS voice files not found at specified paths:")
        print(f"Model: {model_path}")
        print(f"Config: {config_path}")
        print("TTS functionality will be disabled.")

except Exception as e:
    print(f"FATAL ERROR: Could not initialize models or TTS: {e}")
    print(traceback.format_exc())
    # Set to None to prevent errors later and indicate failure
    if embedder is not None: embedder = None # Avoid partially initialized state
    if faiss_index is not None: faiss_index = None
    if tts_voice is not None: tts_voice = None

# --- Core Functions ---

def upload_file(file_obj):
    """ Handles file upload, text extraction, chunking, embedding, and indexing. """
    if embedder is None or faiss_index is None: return "Error: Models not initialized."
    if not file_obj or not hasattr(file_obj, 'name'): return "Error: No file uploaded."
    try:
        faiss_index.reset()
        print("Previous FAISS index cleared.")
        file_path = file_obj.name
        file_basename = os.path.basename(file_path)
        print(f"Processing file: {file_basename}")
        ext = os.path.splitext(file_path)[1].lower()
        if not ext: return f"Error: Could not determine file extension for '{file_basename}'."
        extracted_text = extract_text_from_raw(file_path, ext) # Use updated extractor
        if not extracted_text or not extracted_text.strip(): return f"Error: Could not extract readable text from '{file_basename}'. Check logs."
        chunks = split_text(extracted_text)
        if not chunks: return f"Error: Text extracted but could not be split into chunks."
        print(f"Generating embeddings and indexing {len(chunks)} chunks...")
        count = 0
        for chunk in chunks:
            emb = embedder.get_embedding(chunk)
            if emb is not None: faiss_index.add(emb, chunk); count += 1
            else: print(f"Warning: Could not generate embedding for chunk: {chunk[:100]}...")
        if count == 0: return "Error: Indexing failed. Could not generate embeddings."
        print(f"Successfully indexed {count} chunks from {file_basename}.")
        return f"✅ Uploaded & indexed {count} chunks from '{file_basename}'."
    except Exception as e:
        print(f"Error during file upload/indexing: {e}"); traceback.print_exc()
        return f"❌ An error occurred during processing: {str(e)}."

def ask_question(question):
    """ Handles question, searches, generates text answer, AND generates speech using wave module. """
    audio_filepath = None
    if embedder is None or faiss_index is None: return ["Error: Models not initialized.", None]
    if not question or not question.strip(): return ["Please enter a question.", None]
    if not faiss_index.is_ready(): return ["⚠️ Please upload and index a document first.", None]

    try:
        print(f"Received question: {question}")
        query_emb = embedder.get_embedding(question)
        if query_emb is None: return ["Error: Could not generate embedding for the question.", None]
        top_chunks = faiss_index.search(query_emb, top_k=3)
        if not top_chunks: return ["Could not find relevant context in the document.", None]

        print(f"Found {len(top_chunks)} relevant chunks.")
        context = "\n\n---\n\n".join(top_chunks)
        max_context_len = 2500
        if len(context) > max_context_len: context = context[:max_context_len] + "..."

        prompt = f"""Based *only* on the following context..., answer the question....
Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"""

        print("Generating text answer...")
        answer_text = generate_answer(prompt)
        print("Text answer generated.")

        # --- Generate Speech using wave module ---
        if tts_voice and answer_text:
            model_basename = os.path.basename(model_path) # Get model name for logging
            print(f"Generating speech using {model_basename}...")
            wav_write_obj = None # For finally block
            try:
                # 1. Create a temporary file path (file persists until cleaned up)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_f:
                    audio_filepath = tmp_f.name

                # 2. Open the path with wave module in write binary mode
                wav_write_obj = wave.open(audio_filepath, 'wb')

                # 3. Pass the wave object to piper synthesize
                # Piper will set parameters (framerate etc.) and write frames here
                tts_voice.synthesize(answer_text, wav_write_obj)

                print(f"Speech generated and saved to: {audio_filepath}")

            except Exception as tts_e:
                print(f"Error during TTS synthesis: {tts_e}")
                traceback.print_exc()
                audio_filepath = None # Ensure path is None on error
                if audio_filepath and os.path.exists(audio_filepath): # Cleanup failed file
                     try: os.remove(audio_filepath); print(f"Cleaned failed audio file: {audio_filepath}")
                     except OSError as e_rem: print(f"Error removing failed audio file {audio_filepath}: {e_rem}")
            finally:
                # 4. Ensure the wave file object is closed to finalize header
                if wav_write_obj:
                    wav_write_obj.close()
        elif not tts_voice:
             print("Skipping speech generation: TTS voice not loaded.")
        # --- End Speech Generation ---

        return [answer_text, audio_filepath]

    except Exception as e:
        print(f"Error during question answering: {e}"); traceback.print_exc()
        return [f"❌ An error occurred: {str(e)}", None]

def run_review_agent(file_obj):
    """ Handles file upload for policy review, runs analysis, returns report file. """
    if not file_obj or not hasattr(file_obj, 'name'): print("Error: No file provided for review."); return None
    try:
        file_path = file_obj.name
        file_basename = os.path.basename(file_path)
        print(f"Starting policy review for: {file_basename}")
        ext = os.path.splitext(file_path)[1].lower()
        if not ext: print(f"Error: Could not determine file extension for '{file_basename}'."); return None
        text = extract_text_from_raw(file_path, ext) # Use updated extractor
        if not text or not text.strip(): print(f"Error: Could not extract text from '{file_basename}' for review."); return None
        df = analyze_policies(text)
        if df is None or df.empty: print("Policy analysis did not produce results."); return None
        report_path = "review_report.xlsx"
        df.to_excel(report_path, index=False)
        print(f"Policy review complete. Report saved to {report_path}")
        return report_path
    except Exception as e:
        print(f"Error during policy review: {e}"); traceback.print_exc()
        return None


# --- Gradio Interface Setup ---
upload_input = gr.File(label="Upload Document", file_types=[".txt", ".pdf", ".docx"])
upload_output = gr.Textbox(label="Indexing Status", interactive=False)
qa_input = gr.Textbox(lines=3, placeholder="Enter your question here...", label="Ask a Question")
qa_output_text = gr.Textbox(label="Answer", interactive=False)
qa_output_audio = gr.Audio(label="Spoken Answer (en_US-danny-low)", type="filepath", autoplay=False)
review_input = gr.File(label="Upload Policy Document", file_types=[".txt", ".pdf", ".docx"])
review_output = gr.File(label="Download Review Report")

upload_ui = gr.Interface(fn=upload_file, inputs=upload_input, outputs=upload_output, title="📄 1. Upload & Index")
query_ui = gr.Interface(fn=ask_question, inputs=qa_input, outputs=[qa_output_text, qa_output_audio], title="💬 2. Ask Question")
review_ui = gr.Interface(fn=run_review_agent, inputs=review_input, outputs=review_output, title="📋 3. Policy Review")

app = gr.TabbedInterface([upload_ui, query_ui, review_ui], ["Upload & Index", "Ask Question", "Review Policy"])

# --- Launch the App ---
if __name__ == "__main__":
    print("Launching Gradio App...")
    if embedder is not None and faiss_index is not None:
        app.launch(
            show_error=True,
            server_name="0.0.0.0",   # 👈 Add this line
            server_port=7860
        )
    else:
        print("-----------------------------------------------------")
        print("ERROR: Cannot launch - models failed init.")
        print("-----------------------------------------------------")
        