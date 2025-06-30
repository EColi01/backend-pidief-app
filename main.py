from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfMerger
import io

# Crear la app FastAPI
app = FastAPI()

# Configurar CORS para permitir conexión desde tu frontend en Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-pidief-app.vercel.app"],  # 👈 tu dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de prueba para confirmar que el backend funciona
@app.get("/")
def home():
    return {"mensaje": "Backend de Pidief funcionando"}

# Ruta POST para unir PDFs
@app.post("/unir-pdf/")
async def unir_pdfs(files: List[UploadFile] = File(...)):
    merger = PdfMerger()

    for file in files:
        contenido = await file.read()
        merger.append(io.BytesIO(contenido))

    salida = io.BytesIO()
    merger.write(salida)
    merger.close()
    salida.seek(0)

    # Responder con el PDF unido como descarga
    return StreamingResponse(
        salida,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=unido.pdf"},
    )
