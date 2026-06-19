"""
Service de génération de QR Codes et Barcodes.
"""
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, RadialGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile
from apps.qr_codes.models import QRCode, Barcode
from apps.products.models import Product


class QRCodeService:
    """Service de gestion des QR Codes et Barcodes."""
    
    PRIMARY_COLOR = '#1e40af'
    ACCENT_COLOR = '#ca8a04'
    BACKGROUND_COLOR = '#ffffff'
    
    @staticmethod
    def generate_qr_code(product: Product) -> QRCode:
        """Génère un QR code pour un produit."""
        
        # Contenu du QR code
        qr_data = {
            'type': 'product',
            'id': str(product.id),
            'reference': product.reference,
            'name': product.name,
            'sku': product.sku,
        }
        
        import json
        qr_content = json.dumps(qr_data)
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Image avec style
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(
                front_color=QRCodeService._hex_to_rgb(QRCodeService.PRIMARY_COLOR),
                back_color=QRCodeService._hex_to_rgb(QRCodeService.BACKGROUND_COLOR),
            ),
        )
        
        # Ajouter le logo IUC au centre (optionnel)
        img = QRCodeService._add_center_logo(img, product)
        
        # Sauvegarder l'image
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Créer ou mettre à jour le QR code
        qr_code, created = QRCode.objects.update_or_create(
            product=product,
            defaults={
                'code': qr_content,
                'is_active': True,
            }
        )
        
        qr_code.image.save(
            f'qr_{product.reference}.png',
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        return qr_code
    
    @staticmethod
    def generate_barcode(product: Product, format: str = 'CODE128') -> Barcode:
        """Génère un code-barres pour un produit."""
        
        barcode_data = product.sku or product.reference
        
        # Mapping des formats
        barcode_class = {
            'CODE128': barcode.Code128,
            'CODE39': barcode.Code39,
            'EAN13': barcode.EAN13,
            'EAN8': barcode.EAN8,
        }.get(format, barcode.Code128)
        
        # Générer le code-barres
        buffer = io.BytesIO()
        
        try:
            code = barcode_class(barcode_data, writer=ImageWriter())
            code.write(buffer)
        except Exception:
            # Fallback sur code128 si le format n'est pas compatible
            code = barcode.Code128(product.reference, writer=ImageWriter())
            code.write(buffer)
            format = 'CODE128'
        
        buffer.seek(0)
        
        # Créer ou mettre à jour
        barcode_obj, created = Barcode.objects.update_or_create(
            product=product,
            code=barcode_data,
            format=format,
            defaults={'is_primary': not Barcode.objects.filter(product=product, is_primary=True).exists()}
        )
        
        barcode_obj.image.save(
            f'barcode_{product.reference}.png',
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        return barcode_obj
    
    @staticmethod
    def generate_bulk_qr_codes(product_ids: list) -> bytes:
        """Génère une planche de QR codes pour impression."""
        products = Product.objects.filter(id__in=product_ids, is_deleted=False)
        
        # Créer une planche A4
        a4_width = 2480  # 300 DPI
        a4_height = 3508
        margin = 80
        cols = 4
        rows = 6
        
        cell_width = (a4_width - 2 * margin) // cols
        cell_height = (a4_height - 2 * margin) // rows
        
        canvas = Image.new('RGB', (a4_width, a4_height), 'white')
        draw = ImageDraw.Draw(canvas)
        
        x, y = margin, margin
        count = 0
        
        for product in products:
            if count >= cols * rows:
                break
            
            # Générer le QR code
            qr = qrcode.QRCode(version=1, box_size=6, border=1)
            qr.add_data(f"{product.reference}|{product.name}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color='black', back_color='white')
            qr_img = qr_img.resize((cell_height - 60, cell_height - 60))
            
            # Position
            qr_x = x + (cell_width - qr_img.width) // 2
            qr_y = y + 10
            
            canvas.paste(qr_img, (qr_x, qr_y))
            
            # Texte
            draw.text(
                (x + 10, qr_y + qr_img.height + 5),
                product.name[:30],
                fill='black'
            )
            draw.text(
                (x + 10, qr_y + qr_img.height + 25),
                product.reference,
                fill='gray'
            )
            
            x += cell_width
            count += 1
            
            if count % cols == 0:
                x = margin
                y += cell_height
        
        buffer = io.BytesIO()
        canvas.save(buffer, format='PNG', dpi=(300, 300))
        buffer.seek(0)
        
        return buffer.getvalue()
    
    @staticmethod
    def get_product_by_qr(code: str) -> Product:
        """Récupère un produit à partir d'un QR code scanné."""
        import json
        try:
            data = json.loads(code)
            product_id = data.get('id')
            if product_id:
                return Product.objects.get(id=product_id, is_deleted=False)
        except (json.JSONDecodeError, Product.DoesNotExist):
            pass
        
        # Essayer par référence
        try:
            return Product.objects.get(reference=code, is_deleted=False)
        except Product.DoesNotExist:
            pass
        
        # Essayer par SKU
        try:
            return Product.objects.get(sku=code, is_deleted=False)
        except Product.DoesNotExist:
            pass
        
        return None
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """Convertit une couleur hex en RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def _add_center_logo(img: Image.Image, product: Product) -> Image.Image:
        """Ajoute un logo ou texte au centre du QR code."""
        size = img.size
        center_size = min(size) // 4
        
        # Fond blanc au centre
        draw = ImageDraw.Draw(img)
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        # Carré blanc
        draw.rounded_rectangle(
            [
                center_x - center_size // 2,
                center_y - center_size // 2,
                center_x + center_size // 2,
                center_y + center_size // 2,
            ],
            fill='white',
            radius=10,
        )
        
        return img