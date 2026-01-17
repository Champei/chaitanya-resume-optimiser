from fastapi import FastAPI, UploadFile, File, Form
from ats_engine import ATSSystem
from document_loader import load_resume

app = FastAPI()
ats = ATSSystem()

@app.post("/analyze")
async def analyze(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_text = load_resume(await resume_file.read(), resume_file.filename)
    return ats.analyze(resume_text, job_description)
