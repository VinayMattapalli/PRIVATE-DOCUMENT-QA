from llama_cpp import Llama

# Load the quantized phi-2 model (adjust n_threads if needed)
llm = Llama(
    model_path="models/phi-2/phi-2.gguf.q4_K_M.bin",
    n_ctx=2048,
    n_threads=4
)

def generate_answer(prompt: str) -> str:
    output = llm(prompt, max_tokens=256, stop=["</s>"])
    return output["choices"][0]["text"].strip()
