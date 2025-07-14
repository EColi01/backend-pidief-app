from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import io
import json

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
async def unir_pdfs(
    files: List[UploadFile] = File(...), 
    rotations: str = Form(None)
):
    merger = PdfMerger()
    rotation_values = {}
    
    if rotations:
        try:
            rotation_values = json.loads(rotations)
        except:
            pass

    for i, file in enumerate(files):
        contents = await file.read()
        pdf_bytes = io.BytesIO(contents)
        
        # Check if we need to rotate this PDF
        file_id = str(i)
        if file_id in rotation_values and rotation_values[file_id] != 0:
            rotation_angle = rotation_values[file_id]
            
            # Create a new rotated PDF
            reader = PdfReader(pdf_bytes)
            writer = PdfWriter()
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page.rotate(rotation_angle)
                writer.add_page(page)
            
            rotated_pdf = io.BytesIO()
            writer.write(rotated_pdf)
            rotated_pdf.seek(0)
            merger.append(rotated_pdf)
        else:
            # No rotation needed, append normally
            pdf_bytes.seek(0)
            merger.append(pdf_bytes)

    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=unido.pdf"},
    )