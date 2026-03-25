from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

model_name = "google/gemma-2b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype=torch.float16,
    device_map="auto"
)

class InputText(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Text generation server running"}

@app.post("/generate")
def generate(data: InputText):
    inputs = tokenizer(data.text, return_tensors="pt").to(model.device)
    output = model.generate(
        **inputs,
        max_length=100,
        temperature=0.7,
        do_sample=True
    )
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"response": response}

#uvicorn server:app --host 0.0.0.0 --port 8090 --reload