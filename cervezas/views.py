from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from rest_framework.views import APIView
from .models import Receta, Ingrediente, DetalleIngredientes, TipoIngrediente
from .serializers import RecetaSerializer, IngredienteConRecetaSerializer, AsignarIngredienteSerializer, IngredienteSerializer, TipoConIngredientesSerializer, RecetaConIngredientesSerializer, PrepararBebidaSerializer, CrearRecetaConIngredientesSerializer, EditarRecetaConIngredientesSerializer
from django.db import  IntegrityError
import traceback

class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()

    def get_serializer_class(self):
        # Detalle: GET /recetas/{id}/
        if self.action == 'retrieve':
            return RecetaConIngredientesSerializer
        # Acciones personalizadas
        if self.action == 'crear_con_ingredientes':
            return CrearRecetaConIngredientesSerializer
        if self.action in ('editar_con_ingredientes',):
            return EditarRecetaConIngredientesSerializer
        # CRUD base
        return RecetaSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == 'retrieve':
            ctx['receta'] = self.get_object()
        return ctx

    # POST /recetas/crear-con-ingredientes/
    @action(detail=False, methods=['post'], url_path='crear-con-ingredientes')
    def crear_con_ingredientes(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                receta = ser.save()
            data = RecetaConIngredientesSerializer(receta, context={'receta': receta}).data
            return Response(data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            # p.ej. violación unique_together o FK
            return Response({"error": f"Integridad: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # log completo en consola + error legible al cliente
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # PUT/PATCH /recetas/{id}/editar-con-ingredientes/
    @action(detail=True, methods=['put', 'patch'], url_path='editar-con-ingredientes')
    def editar_con_ingredientes(self, request, *args, **kwargs):
        receta = self.get_object()
        partial = request.method.lower() == 'patch'
        ser = self.get_serializer(receta, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                receta = ser.save()
            data = RecetaConIngredientesSerializer(receta, context={'receta': receta}).data
            return Response(data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": f"Integridad: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
    @transaction.atomic
    def post(self, request):
        serializer = PrepararBebidaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        receta_id = serializer.validated_data['receta_id']
        cantidad_preparar = serializer.validated_data['cantidad']
        # Si cantidad_preparar es int, conviértelo a Decimal para operar
        if isinstance(cantidad_preparar, int):
            cantidad_preparar = Decimal(cantidad_preparar)

        try:
            detalles = (DetalleIngredientes.objects
                        .select_related('ingrediente')
                        .filter(receta_id=receta_id))
            if not detalles.exists():
                return Response({"error": "La receta no tiene ingredientes asignados."}, status=400)

            # 1) Validación de stock con Decimal
            for d in detalles:
                requerido = d.cantidad * cantidad_preparar  # Decimal * Decimal
                if d.ingrediente.stock < requerido:
                    return Response({
                        "error": (
                            f"No hay suficiente stock de {d.ingrediente.nombre_ingrediente}. "
                            f"Requiere {requerido}, disponible {d.ingrediente.stock}"
                        )
                    }, status=400)

            # 2) Descuento de stock — opción simple (con reload por si hay race conditions)
            for d in detalles:
                requerido = d.cantidad * cantidad_preparar
                ing = d.ingrediente
                # Relee y actualiza atómicamente con F para minimizar condiciones de carrera
                updated = (Ingrediente.objects
                           .filter(pk=ing.pk, stock__gte=requerido)
                           .update(stock=F('stock') - requerido))
                if not updated:
                    # Si alguien consumió stock en paralelo
                    raise ValueError(f"Stock insuficiente para {ing.nombre_ingrediente} durante la operación.")

            return Response({"mensaje": "Bebida preparada exitosamente."})

        except Receta.DoesNotExist:
            return Response({"error": "Receta no encontrada."}, status=404)
        except ValueError as ex:
            return Response({"error": str(ex)}, status=400)