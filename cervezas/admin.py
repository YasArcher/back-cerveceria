from django.contrib import admin
from .models import (
    TipoIngrediente,
    UnidadMedida,
    Ingrediente,
    Receta,
    DetalleIngredientes,
)

admin.site.register(TipoIngrediente)
admin.site.register(UnidadMedida)
admin.site.register(Ingrediente)
admin.site.register(Receta)
admin.site.register(DetalleIngredientes)
