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

@app.post("/dividir-pdf/")
async def dividir_pdf(
    file: UploadFile = File(...),
    selected_pages: str = Form(...)
):
    # Read the uploaded PDF
    contents = await file.read()
    pdf_bytes = io.BytesIO(contents)
    reader = PdfReader(pdf_bytes)
    
    # Parse selected pages
    try:
        selected_pages_list = json.loads(selected_pages)
    except:
        selected_pages_list = []
    
    if not selected_pages_list:
        return {"error": "No se seleccionaron páginas"}
    
    # Create a new PDF with only the selected pages
    writer = PdfWriter()
    
    # Extract each selected page
    for page_num in selected_pages_list:
        # PyPDF2 uses 0-based indexing, but frontend likely uses 1-based indexing
        page_index = int(page_num) - 1 if isinstance(page_num, (int, str)) else page_num
        
        if 0 <= page_index < len(reader.pages):
            page = reader.pages[page_index]
            writer.add_page(page)
    
    # Write the new PDF to a BytesIO object
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=paginas_divididas.pdf"}
    )