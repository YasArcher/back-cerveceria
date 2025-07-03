from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecetaViewSet, IngredienteExtendidoViewSet, AsignarIngredienteViewSet, IngredienteViewSet, TipoConIngredientesViewSet, RecetaConIngredientesViewSet, PrepararBebidaView

router = DefaultRouter()
router.register(r'recetas', RecetaViewSet)
router.register(r'ingredientes-avanzado', IngredienteExtendidoViewSet, basename='ingredientes-avanzado')
router.register(r'detalle-ingredientes', AsignarIngredienteViewSet)
router.register(r'ingredientes', IngredienteViewSet)
router.register(r'tipos-con-ingredientes', TipoConIngredientesViewSet)
router.register(r'recetas-con-ingredientes', RecetaConIngredientesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('preparar-bebida/', PrepararBebidaView.as_view(), name='preparar-bebida'),
]
