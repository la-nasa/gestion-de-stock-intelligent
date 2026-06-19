"""
Modèles pour les QR Codes et Barcodes.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class QRCode(BaseModel):
    """QR Code pour un produit/équipement."""

    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='qr_code',
        verbose_name=_('produit')
    )
    code = models.CharField(
        _('code QR'),
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Contenu encodé dans le QR code"
    )
    image = models.ImageField(
        _('image QR code'),
        upload_to='qrcodes/%Y/%m/',
        blank=True,
        null=True
    )
    generated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('généré par')
    )
    last_scanned_at = models.DateTimeField(
        _('dernier scan'),
        null=True,
        blank=True
    )
    scan_count = models.IntegerField(_('nombre de scans'), default=0)
    is_active = models.BooleanField(_('actif'), default=True)

    class Meta:
        verbose_name = _('QR code')
        verbose_name_plural = _('QR codes')
        ordering = ['-created_at']

    def __str__(self):
        return f"QR-{self.product.reference}"

    def increment_scan(self):
        from django.utils import timezone
        self.scan_count += 1
        self.last_scanned_at = timezone.now()
        self.save(update_fields=['scan_count', 'last_scanned_at'])


class Barcode(BaseModel):
    """Code-barres pour un produit."""

    class Format(models.TextChoices):
        CODE128 = 'CODE128', _('Code 128')
        CODE39 = 'CODE39', _('Code 39')
        EAN13 = 'EAN13', _('EAN-13')
        EAN8 = 'EAN8', _('EAN-8')
        UPC = 'UPC', _('UPC')
        QR = 'QR', _('QR Code')

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='barcodes',
        verbose_name=_('produit')
    )
    code = models.CharField(
        _('code-barres'),
        max_length=255,
        unique=True,
        db_index=True
    )
    format = models.CharField(
        _('format'),
        max_length=20,
        choices=Format.choices,
        default=Format.CODE128
    )
    image = models.ImageField(
        _('image code-barres'),
        upload_to='barcodes/%Y/%m/',
        blank=True,
        null=True
    )
    is_primary = models.BooleanField(_('principal'), default=False)
    notes = models.CharField(_('notes'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('code-barres')
        verbose_name_plural = _('codes-barres')
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['product', 'is_primary']),
        ]

    def __str__(self):
        return f"{self.format}: {self.code}"

    def save(self, *args, **kwargs):
        # S'assurer qu'un seul code-barres principal par produit
        if self.is_primary:
            Barcode.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class QRScanLog(BaseModel):
    """Historique des scans de QR codes."""

    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name='scan_logs',
        verbose_name=_('QR code')
    )
    scanned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('scanné par')
    )
    ip_address = models.GenericIPAddressField(
        _('adresse IP'),
        null=True,
        blank=True
    )
    device_info = models.CharField(
        _('appareil'),
        max_length=255,
        blank=True
    )
    location = models.CharField(
        _('localisation'),
        max_length=255,
        blank=True
    )
    action = models.CharField(
        _('action'),
        max_length=50,
        blank=True,
        help_text="Action déclenchée par le scan"
    )

    class Meta:
        verbose_name = _('log de scan')
        verbose_name_plural = _('logs de scan')
        ordering = ['-created_at']

    def __str__(self):
        return f"Scan {self.qr_code.code} - {self.created_at}"
