from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

# This is a long document we can split up.
with open("./input/1.txt") as f:
    doc_1 = f.read()
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer, chunk_size=100, chunk_overlap=0
)

texts = text_splitter.split_text(doc_1)

for x, text in enumerate(texts):
    print(f"{x}-{text}")