"""Routes OCR du microservice ML."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional

router = APIRouter()


@router.post("/extract")
async def extract_invoice_data(
    file: UploadFile = File(...),
    language: str = "fr",
    enhance: bool = True,
):
    """Extrait les données d'une facture par OCR."""
    
    # Vérifier le type de fichier
    if file.content_type not in [
        "image/jpeg", "image/png", "image/tiff",
        "image/bmp", "application/pdf"
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté: {file.content_type}"
        )
    
    try:
        # Lire le fichier
        content = await file.read()
        
        # Simulation OCR (à remplacer par vrai OCR)
        import random
        from datetime import datetime
        
        return {
            "filename": file.filename,
            "extraction_date": datetime.now().isoformat(),
            "confidence": round(random.uniform(0.7, 0.98), 2),
            "invoice_data": {
                "invoice_number": f"FACT-{random.randint(1000, 9999)}",
                "date": f"2026-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
                "supplier": {
                    "name": "Fournisseur Exemple",
                    "tax_id": f"TX{random.randint(10000, 99999)}",
                },
                "amounts": {
                    "subtotal": round(random.uniform(50000, 500000), 2),
                    "tax": round(random.uniform(5000, 50000), 2),
                    "total": round(random.uniform(55000, 550000), 2),
                },
                "items": [
                    {
                        "description": f"Article {i+1}",
                        "quantity": random.randint(1, 50),
                        "unit_price": round(random.uniform(1000, 50000), 2),
                        "total": round(random.uniform(50000, 500000), 2),
                    }
                    for i in range(random.randint(2, 5))
                ],
            },
            "raw_text_sample": "FACTURE N°... (aperçu du texte extrait)",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engines")
async def list_ocr_engines():
    """Liste les moteurs OCR disponibles."""
    return {
        "engines": [
            {
                "name": "easyocr",
                "description": "EasyOCR - Deep learning based",
                "languages": ["fr", "en", "ar", "zh"],
                "gpu_support": True,
                "status": "available",
            },
            {
                "name": "tesseract",
                "description": "Tesseract OCR - Open source",
                "languages": ["fra", "eng", "ara"],
                "gpu_support": False,
                "status": "available",
            },
        ]
    }