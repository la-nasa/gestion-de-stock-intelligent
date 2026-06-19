"""
Service d'OCR pour l'extraction de données de factures.
Utilise EasyOCR et Tesseract comme fallback.
"""
import io
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from PIL import Image
import numpy as np

# Try imports with fallbacks
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRService:
    """Service d'extraction de données de factures par OCR."""
    
    # Patterns pour extraction
    PATTERNS = {
        'invoice_number': [
            r'(?:facture|invoice|fact)\s*(?:n[°o]|num[ée]ro|#)?\s*[:.]?\s*([A-Z0-9\-/]+)',
            r'(?:n[°o]|num[ée]ro)\s*(?:de\s*)?(?:facture|fact)\s*[:.]?\s*([A-Z0-9\-/]+)',
        ],
        'date': [
            r'(?:date|datedu)\s*[:.]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
        ],
        'supplier': [
            r'(?:fournisseur|supplier|vendeur|émetteur)\s*[:.]?\s*(.+)',
            r'(?:soci[ée]t[ée]|entreprise|company)\s*[:.]?\s*(.+)',
        ],
        'supplier_tax_id': [
            r'(?:ninea|tax\s*id|tva|vat|siret)\s*[:.]?\s*([A-Z0-9\s]+)',
        ],
        'total_amount': [
            r'(?:total|montant\s*total|net\s*[àa]\s*payer)\s*[:.]?\s*([\d\s,.]+)\s*(?:XAF|FCFA|€|EUR|USD)?',
            r'(?:total\s*ttc|ttc)\s*[:.]?\s*([\d\s,.]+)',
        ],
        'subtotal': [
            r'(?:sous[-\s]?total|ht|hors\s*taxe)\s*[:.]?\s*([\d\s,.]+)',
        ],
        'tax_amount': [
            r'(?:tva|taxe)\s*[:.]?\s*([\d\s,.]+)',
        ],
        'items': [
            r'(\d+)\s*x\s*(.+?)\s*[àa]\s*([\d\s,.]+)\s*(?:XAF|FCFA)?',
        ],
    }
    
    # Mots-clés pour identifier les colonnes d'un tableau
    TABLE_HEADERS = [
        'désignation', 'designation', 'description', 'article', 'produit',
        'quantité', 'quantite', 'qte', 'qty', 'quantity',
        'prix', 'price', 'pu', 'prix unitaire', 'unit price',
        'montant', 'amount', 'total',
    ]
    
    @classmethod
    def extract_invoice_data(cls, image_data: bytes) -> Dict[str, Any]:
        """Extrait les données d'une facture à partir d'une image."""
        
        # Charger l'image
        image = Image.open(io.BytesIO(image_data))
        
        # Prétraitement
        image = cls._preprocess_image(image)
        
        # OCR
        text = cls._perform_ocr(image)
        
        # Extraction des données
        result = cls._extract_fields(text)
        
        # Extraction des lignes d'articles
        result['items'] = cls._extract_line_items(text)
        
        # Métadonnées
        result['raw_text'] = text[:500]  # Garder les 500 premiers caractères
        result['confidence'] = cls._estimate_confidence(result)
        result['extraction_date'] = datetime.now().isoformat()
        
        return result
    
    @classmethod
    def _preprocess_image(cls, image: Image.Image) -> Image.Image:
        """Prétraitement de l'image pour améliorer l'OCR."""
        import numpy as np
        
        # Convertir en niveaux de gris
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convertir en array numpy
        img_array = np.array(image)
        
        # Améliorer le contraste
        min_val = np.min(img_array)
        max_val = np.max(img_array)
        if max_val > min_val:
            img_array = ((img_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        # Binarisation adaptative
        threshold = np.mean(img_array)
        img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    @classmethod
    def _perform_ocr(cls, image: Image.Image) -> str:
        """Effectue l'OCR sur l'image."""
        text_parts = []
        
        # Essayer EasyOCR d'abord
        if EASYOCR_AVAILABLE:
            try:
                reader = easyocr.Reader(['fr', 'en'], gpu=False)
                results = reader.readtext(np.array(image))
                text_parts = [result[1] for result in results]
                return '\n'.join(text_parts)
            except Exception as e:
                pass
        
        # Fallback sur Tesseract
        if TESSERACT_AVAILABLE:
            try:
                text = pytesseract.image_to_string(image, lang='fra+eng')
                return text
            except Exception as e:
                pass
        
        # Si aucun OCR n'est disponible
        if not text_parts:
            return "OCR non disponible. Veuillez installer EasyOCR ou Tesseract."
        
        return '\n'.join(text_parts)
    
    @classmethod
    def _extract_fields(cls, text: str) -> Dict[str, Any]:
        """Extrait les champs clés du texte OCR."""
        text_lower = text.lower()
        result = {}
        
        # Numéro de facture
        result['invoice_number'] = cls._find_pattern(text_lower, cls.PATTERNS['invoice_number'])
        
        # Date
        date_str = cls._find_pattern(text_lower, cls.PATTERNS['date'])
        result['date'] = cls._parse_date(date_str) if date_str else None
        
        # Fournisseur
        result['supplier_name'] = cls._find_pattern(text_lower, cls.PATTERNS['supplier'])
        result['supplier_tax_id'] = cls._find_pattern(text_lower, cls.PATTERNS['supplier_tax_id'])
        
        # Montants
        result['total_amount'] = cls._parse_amount(cls._find_pattern(text_lower, cls.PATTERNS['total_amount']))
        result['subtotal'] = cls._parse_amount(cls._find_pattern(text_lower, cls.PATTERNS['subtotal']))
        result['tax_amount'] = cls._parse_amount(cls._find_pattern(text_lower, cls.PATTERNS['tax_amount']))
        
        return result
    
    @classmethod
    def _extract_line_items(cls, text: str) -> List[Dict[str, Any]]:
        """Extrait les lignes d'articles de la facture."""
        items = []
        lines = text.split('\n')
        
        # Chercher la section tableau
        in_table = False
        table_started = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Détecter le début du tableau
            if not table_started:
                header_matches = sum(1 for h in cls.TABLE_HEADERS if h in line_lower)
                if header_matches >= 2:
                    table_started = True
                    continue
            
            if table_started:
                # Essayer d'extraire quantité, description, prix
                item = cls._parse_item_line(line)
                if item:
                    items.append(item)
                
                # Détecter la fin du tableau (ligne de total)
                if any(word in line_lower for word in ['total', 'ttc', 'net à payer', 'sous-total']):
                    break
        
        return items
    
    @classmethod
    def _parse_item_line(cls, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne d'article."""
        # Pattern: Quantité x Description @ Prix unitaire
        match = re.search(r'(\d+)\s*x\s*(.+?)\s*(?:@|[àa])\s*([\d\s,.]+)', line, re.IGNORECASE)
        if match:
            return {
                'quantity': int(match.group(1)),
                'description': match.group(2).strip(),
                'unit_price': cls._parse_amount(match.group(3)),
            }
        
        # Pattern: Description - Qté: X - PU: Y
        qty_match = re.search(r'(?:qt[ée]|quantit[ée])\s*[:.]?\s*(\d+)', line, re.IGNORECASE)
        price_match = re.search(r'(?:pu|prix)\s*[:.]?\s*([\d\s,.]+)', line, re.IGNORECASE)
        desc_match = re.search(r'^([a-zA-Z0-9\s\-]+?)(?:\s*(?:qt[ée]|quantit[ée]|pu|prix))', line, re.IGNORECASE)
        
        if qty_match or price_match:
            return {
                'quantity': int(qty_match.group(1)) if qty_match else 1,
                'description': desc_match.group(1).strip() if desc_match else line.strip(),
                'unit_price': cls._parse_amount(price_match.group(1)) if price_match else 0,
            }
        
        return None
    
    @classmethod
    def _find_pattern(cls, text: str, patterns: List[str]) -> Optional[str]:
        """Recherche un pattern dans le texte."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    @classmethod
    def _parse_amount(cls, value: str) -> Optional[float]:
        """Parse un montant."""
        if not value:
            return None
        
        # Nettoyer la valeur
        value = value.replace(' ', '').replace('\xa0', '')
        
        # Gérer les formats français (1.234,56) et anglais (1,234.56)
        if ',' in value and '.' in value:
            # Déterminer le format
            if value.rfind(',') > value.rfind('.'):
                # Format français: 1.234,56
                value = value.replace('.', '').replace(',', '.')
            else:
                # Format anglais: 1,234.56
                value = value.replace(',', '')
        elif ',' in value:
            # Peut être 1234,56 ou 1,234
            if len(value.split(',')[-1]) <= 2:
                value = value.replace(',', '.')
            else:
                value = value.replace(',', '')
        
        try:
            return float(value)
        except ValueError:
            return None
    
    @classmethod
    def _parse_date(cls, date_str: str) -> Optional[str]:
        """Parse une date."""
        if not date_str:
            return None
        
        # Essayer différents formats
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%d/%m/%y', '%d-%m-%y',
            '%Y/%m/%d', '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str
    
    @classmethod
    def _estimate_confidence(cls, result: Dict[str, Any]) -> float:
        """Estime la confiance de l'extraction."""
        score = 0
        total_fields = 0
        
        # Chaque champ trouvé augmente la confiance
        if result.get('invoice_number'):
            score += 1
        total_fields += 1
        
        if result.get('date'):
            score += 1
        total_fields += 1
        
        if result.get('supplier_name'):
            score += 1
        total_fields += 1
        
        if result.get('total_amount'):
            score += 1
        total_fields += 1
        
        if result.get('items') and len(result['items']) > 0:
            score += 1
        total_fields += 1
        
        return round(score / max(total_fields, 1), 2)