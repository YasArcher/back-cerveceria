from django.db import models
from decimal import Decimal

class TipoIngrediente(models.Model):
    nombre_tipo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_tipo


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    nombre_ingrediente = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoIngrediente, on_delete=models.CASCADE)
    unidad = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    stock = models.FloatField()

    def __str__(self):
        return self.nombre_ingrediente


class Receta(models.Model):
    nombre_receta = models.CharField(max_length=100)
    descripcion = models.TextField()
    porcentaje_alcohol = models.FloatField()
    contenido_neto = models.FloatField()
    imagen = models.ImageField(upload_to='recetas/', blank=True, null=True)

    def __str__(self):
        return self.nombre_receta


class DetalleIngredientes(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.receta} - {self.ingrediente} ({self.cantidad})"

