from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import uuid
import torch
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RhymesAI Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and tokenizer
model_name = "devyatilov/trained_rugpt3_rhyme_large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
device = torch.device("cpu")  # Force CPU
model.to(device)

# In-memory task storage
tasks = {}

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    task_id: str

class StatusResponse(BaseModel):
    status: str
    response: str = None

def generate_rhyme(prompt, max_length=100):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_length=max_length,  # Increased slightly for larger model
        num_beams=5,  # Slightly increased for better rhyme quality
        no_repeat_ngram_size=2,
        do_sample=True,
        top_p=0.9,
        temperature=0.8,
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "response": None}
    try:
        rhyme = generate_rhyme(request.prompt)
        tasks[task_id] = {"status": "completed", "response": rhyme}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "response": str(e)}
    return GenerateResponse(task_id=task_id)

@app.get("/status/{task_id}", response_model=StatusResponse)
async def check_status(task_id: str):
    task_data = tasks.get(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return StatusResponse(**task_data)