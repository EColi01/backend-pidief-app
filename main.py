from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfMerger
import io

# Crear la app FastAPI
app = FastAPI()

# Configurar CORS correctamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-pidief-app.vercel.app"],  # Tu frontend en Vercel
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos: GET, POST, etc.
    allow_headers=["*"],  # Permite todos los headers
)

# Ruta de prueba para verificar que el backend está funcionando
@app.get("/")
def home():
    return {"mensaje": "Backend de Pidief funcionando"}

# Ruta para unir múltiples archivos PDF
@app.post("/unir-pdf/")
async def unir_pdfs(archivos: List[UploadFile] = File(...)):
    merger = PdfMerger()

    for archivo in archivos:
        contenido = await archivo.read()
        merger.append(io.BytesIO(contenido))

    salida = io.BytesIO()
    merger.write(salida)
    merger.close()
    salida.seek(0)

    return StreamingResponse(
        salida,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=unido.pdf"},
    )
