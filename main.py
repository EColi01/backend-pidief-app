from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfMerger
import io

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-pidief-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Servidor funcionando"}

@app.post("/unir-pdf/")
async def unir_pdfs(files: List[UploadFile] = File(...)):
    merger = PdfMerger()

    for file in files:
        contents = await file.read()
        merger.append(io.BytesIO(contents))

    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=unido.pdf"},
    )
