from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PyPDF2 import PdfMerger
import os
import uuid

app = FastAPI()

# Permitir solicitudes desde tu frontend (React en Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-pdf-app.vercel.app/"],  # En producción: cambiar "*" por tu dominio de Vercel
    allow_credentials=True,
    allow_methods=["https://frontend-pdf-app.vercel.app/"],
    allow_headers=["https://frontend-pdf-app.vercel.app/"],
)

@app.post("/unir-pdf/")

@app.get("/")
def root():
    return {"mensaje": "Backend de Pidief funcionando"}

@app.post("/unir-pdf/")
async def unir_pdfs(files: list[UploadFile] = File(...)):
    """
    Recibe múltiples archivos PDF, los une en uno solo y lo devuelve.
    """

    # Crear un nombre único para el PDF resultante
    output_filename = f"{uuid.uuid4()}.pdf"

    # Crear el combinador de PDFs
    merger = PdfMerger()

    # Guardar temporalmente los archivos recibidos
    for file in files:
        contents = await file.read()
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as f:
            f.write(contents)
        merger.append(temp_filename)

    # Guardar el PDF final
    with open(output_filename, "wb") as f:
        merger.write(f)

    # Limpiar archivos temporales
    for file in files:
        os.remove(f"temp_{file.filename}")

    # Devolver el PDF unido como archivo descargable
    return FileResponse(output_filename, filename="pidief-unido.pdf", media_type="application/pdf")
