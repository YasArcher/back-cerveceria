from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Receta, Ingrediente, DetalleIngredientes, TipoIngrediente
from .serializers import RecetaSerializer, IngredienteConRecetaSerializer, AsignarIngredienteSerializer, IngredienteSerializer, TipoConIngredientesSerializer, RecetaConIngredientesSerializer, PrepararBebidaSerializer

# 🔹 Vista para Recetas
class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer

class IngredienteViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer

# 🔹 Vista para crear Ingredientes (y opcionalmente asociarlos a una receta)
class IngredienteExtendidoViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteConRecetaSerializer

class AsignarIngredienteViewSet(viewsets.ModelViewSet):
    queryset = DetalleIngredientes.objects.all()
    serializer_class = AsignarIngredienteSerializer

class TipoConIngredientesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoIngrediente.objects.all()
    serializer_class = TipoConIngredientesSerializer

class RecetaConIngredientesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaConIngredientesSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'retrieve':
            context['receta'] = self.get_object()
        elif self.action == 'list':
            # Contexto para múltiples recetas: se usa uno por cada instancia al serializar
            context['include_cantidad'] = True
        return context

class PrepararBebidaView(APIView):
    def post(self, request):
        serializer = PrepararBebidaSerializer(data=request.data)
        if serializer.is_valid():
            receta_id = serializer.validated_data['receta_id']
            cantidad_preparar = serializer.validated_data['cantidad']

            try:
                detalles = DetalleIngredientes.objects.filter(receta_id=receta_id).select_related('ingrediente')
                if not detalles.exists():
                    return Response({"error": "La receta no tiene ingredientes asignados."}, status=400)

                # Validar stock disponible
                for detalle in detalles:
                    requerido = detalle.cantidad * cantidad_preparar
                    if detalle.ingrediente.stock < requerido:
                        return Response({
                            "error": f"No hay suficiente stock de {detalle.ingrediente.nombre_ingrediente}. Requiere {requerido}, disponible {detalle.ingrediente.stock}"
                        }, status=400)

                # Restar del stock
                for detalle in detalles:
                    requerido = detalle.cantidad * cantidad_preparar
                    ingrediente = detalle.ingrediente
                    ingrediente.stock -= float(requerido)
                    ingrediente.save()

                return Response({"mensaje": "Bebida preparada exitosamente."})

            except Receta.DoesNotExist:
                return Response({"error": "Receta no encontrada."}, status=404)

        return Response(serializer.errors, status=400)