# models.py
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class TipoIngrediente(models.Model):
    nombre_tipo = models.CharField(max_length=100)
    def __str__(self): return self.nombre_tipo

class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self): return self.nombre

class Ingrediente(models.Model):
    nombre_ingrediente = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoIngrediente, on_delete=models.CASCADE)
    unidad = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)

    # Antes: FloatField -> Ahora: DecimalField
    # max_digits/decimal_places depende de tu negocio; aquí dejo ejemplos comunes
    stock = models.DecimalField(
        max_digits=12, decimal_places=3,  # p.ej. hasta 9.999.999,999
        validators=[MinValueValidator(Decimal('0'))]
    )

    def __str__(self): return self.nombre_ingrediente

class Receta(models.Model):
    nombre_receta = models.CharField(max_length=100)
    descripcion = models.TextField()

    # Antes: FloatField -> Ahora: DecimalField
    porcentaje_alcohol = models.DecimalField(
        max_digits=5, decimal_places=2,               # ej. 0.00 - 100.00
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    contenido_neto = models.DecimalField(
        max_digits=10, decimal_places=2,              # ej. mililitros/litros con 2 decimales
        validators=[MinValueValidator(Decimal('0'))]
    )

    imagen = models.ImageField(upload_to='recetas/', blank=True, null=True)
    def __str__(self): return self.nombre_receta

class DetalleIngredientes(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)  # ya lo tenías en Decimal

    class Meta:
        unique_together = ('receta', 'ingrediente')  # evita duplicados

    def __str__(self):
        return f"{self.receta} - {self.ingrediente} ({self.cantidad})"
