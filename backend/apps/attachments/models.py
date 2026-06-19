"""
Modèles de gestion des pièces jointes.
"""
import os
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models.base import BaseModel


def attachment_upload_path(instance, filename):
    """Génère le chemin d'upload pour les pièces jointes."""
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return f'attachments/{instance.content_type.model}/{instance.object_id}/{new_filename}'


class Attachment(BaseModel):
    """Pièce jointe générique."""

    class FileType(models.TextChoices):
        IMAGE = 'IMAGE', _('Image')
        PDF = 'PDF', _('PDF')
        DOCUMENT = 'DOCUMENT', _('Document')
        SPREADSHEET = 'SPREADSHEET', _('Tableur')
        ARCHIVE = 'ARCHIVE', _('Archive')
        OTHER = 'OTHER', _('Autre')

    # Relation générique
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('type de contenu')
    )
    object_id = models.UUIDField(_('ID objet'))
    content_object = GenericForeignKey('content_type', 'object_id')

    # Fichier
    file = models.FileField(
        _('fichier'),
        upload_to=attachment_upload_path,
        max_length=500
    )
    filename = models.CharField(_('nom du fichier'), max_length=500)
    file_size = models.BigIntegerField(_('taille (octets)'))
    file_type = models.CharField(
        _('type de fichier'),
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER
    )
    mime_type = models.CharField(_('type MIME'), max_length=100, blank=True)
    checksum = models.CharField(
        _('somme de contrôle SHA256'),
        max_length=64,
        blank=True
    )

    # Métadonnées
    title = models.CharField(_('titre'), max_length=300, blank=True)
    description = models.TextField(_('description'), blank=True)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_attachments',
        verbose_name=_('téléchargé par')
    )
    is_public = models.BooleanField(_('public'), default=False)
    download_count = models.IntegerField(_('téléchargements'), default=0)

    class Meta:
        verbose_name = _('pièce jointe')
        verbose_name_plural = _('pièces jointes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = os.path.basename(self.file.name)
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
