from django.db import models
from django.contrib.auth.models import User

class Solicitud(models.Model):
    CATEGORIA_CHOICES = [
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Redes', 'Redes'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Resuelto', 'Resuelto'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default ='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes')

    def __str__(self):
        return f"[{self.id}] {self.titulo} - {self.usuario.username}"
