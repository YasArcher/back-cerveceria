# serializers.py
from decimal import Decimal, InvalidOperation
from django.db import transaction
from rest_framework import serializers
from .models import Ingrediente, DetalleIngredientes, Receta, TipoIngrediente, UnidadMedida

# ─────────────────────────────────────────────────────────────────────
# 📦 Serializers de modelos base
# ─────────────────────────────────────────────────────────────────────

class TipoIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoIngrediente
        fields = ['id', 'nombre_tipo']

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = '__all__'

class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = '__all__'

class IngredienteSerializer(serializers.ModelSerializer):
    # read-only (lo que devolverá la API)
    unidad = UnidadSerializer(read_only=True)
    tipo = TipoIngredienteSerializer(read_only=True)

    # write-only (lo que recibe la API en POST/PATCH)
    unidad_id = serializers.PrimaryKeyRelatedField(
        queryset=UnidadMedida.objects.all(),
        source='unidad',
        write_only=True
    )
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoIngrediente.objects.all(),
        source='tipo',
        write_only=True
    )

    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre_ingrediente', 'stock', 'unidad', 'tipo', 'unidad_id', 'tipo_id']
# ─────────────────────────────────────────────────────────────────────
# 📋 Serializers de lógica personalizada (POST, validaciones)
# ─────────────────────────────────────────────────────────────────────

class IngredienteConRecetaSerializer(serializers.ModelSerializer):
    receta = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre_ingrediente', 'tipo', 'unidad', 'stock', 'receta']

    def create(self, validated_data):
        receta_id = validated_data.pop('receta', None)
        ingrediente = Ingrediente.objects.create(**validated_data)

        if receta_id:
            DetalleIngredientes.objects.create(receta_id=receta_id, ingrediente=ingrediente)

        return ingrediente

class AsignarIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleIngredientes
        fields = ['id', 'receta', 'ingrediente']

    def validate(self, data):
        receta = data.get('receta')
        ingrediente = data.get('ingrediente')
        if DetalleIngredientes.objects.filter(receta=receta, ingrediente=ingrediente).exists():
            raise serializers.ValidationError("Este ingrediente ya está asignado a la receta.")
        return data

# ─────────────────────────────────────────────────────────────────────
# 📘 Serializers para respuestas anidadas o GET personalizados
# ─────────────────────────────────────────────────────────────────────

class IngredienteBasicoSerializer(serializers.ModelSerializer):
    unidad = UnidadSerializer()
    cantidad = serializers.SerializerMethodField()

    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre_ingrediente', 'unidad', 'cantidad', 'stock']

    def get_cantidad(self, ingrediente):
        override = self.context.get('cantidad_override')
        if override is not None:
            return override

        receta = self.context.get('receta')
        if not receta:
            return None
        detalle = DetalleIngredientes.objects.filter(
            receta=receta,
            ingrediente=ingrediente
        ).first()
        return detalle.cantidad if detalle else None

class TipoConIngredientesSerializer(serializers.ModelSerializer):
    ingredientes = serializers.SerializerMethodField()

    class Meta:
        model = TipoIngrediente
        fields = ['id', 'nombre_tipo', 'ingredientes']

    def get_ingredientes(self, obj):
        ingredientes = Ingrediente.objects.filter(tipo=obj)
        return IngredienteBasicoSerializer(ingredientes, many=True).data

# ─────────────────────────────────────────────────────────────────────
# 🍺 Serializer principal: Receta con sus tipos e ingredientes asignados
# ─────────────────────────────────────────────────────────────────────

class TipoIngredienteConIngredientesDeRecetaSerializer(serializers.ModelSerializer):
    ingredientes = serializers.SerializerMethodField()

    class Meta:
        model = TipoIngrediente
        fields = ['id', 'nombre_tipo', 'ingredientes']

    def get_ingredientes(self, tipo):
        receta = self.context.get('receta')
        if not receta:
            return []

        detalles = DetalleIngredientes.objects.select_related('ingrediente').filter(
            receta=receta,
            ingrediente__tipo=tipo
        )

        ingredientes = []
        for detalle in detalles:
            serializer = IngredienteBasicoSerializer(
                detalle.ingrediente,
                context={'receta': receta, 'cantidad_override': detalle.cantidad}
            )
            ingredientes.append(serializer.data)
        return ingredientes

class RecetaConIngredientesSerializer(serializers.ModelSerializer):
    tipos = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = ['id', 'nombre_receta', 'descripcion', 'tipos']

    def get_tipos(self, receta):
        tipos = TipoIngrediente.objects.all()
        return TipoIngredienteConIngredientesDeRecetaSerializer(
            tipos, many=True, context={'receta': receta}
        ).data


# ─────────────────────────────────────────────────────────────────────
# 🍺 Serializer para preparar una bebida
# ─────────────────────────────────────────────────────────────────────

class PrepararBebidaSerializer(serializers.Serializer):
    receta_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
# ─────────────────────────────────────────────────────────────
# Items de ingrediente (entrada)
# ─────────────────────────────────────────────────────────────
class DetalleIngredienteInputSerializer(serializers.Serializer):
    ingrediente_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingrediente.objects.all(),
        source='ingrediente'
    )
    cantidad = serializers.CharField()  # normalizamos abajo

    def validate_cantidad(self, v):
        s = str(v).replace(',', '.')
        try:
            d = Decimal(s)
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("cantidad inválida (use números, ej. 1.50).")
        if d < Decimal('0.01'):
            raise serializers.ValidationError("cantidad mínima 0.01.")
        return d.quantize(Decimal('0.01'))  # 👈 2 decimales

# ─────────────────────────────────────────────────────────────
# Crear Receta con ingredientes
# ─────────────────────────────────────────────────────────────
class CrearRecetaConIngredientesSerializer(serializers.ModelSerializer):
    ingredientes = DetalleIngredienteInputSerializer(many=True, write_only=True)

    class Meta:
        model = Receta
        fields = ['id','nombre_receta','descripcion','porcentaje_alcohol','contenido_neto','imagen','ingredientes']
        read_only_fields = ['id']
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True},
            'porcentaje_alcohol': {'required': False, 'allow_null': True},
            'contenido_neto': {'required': False, 'allow_null': True},
        }

    def validate_ingredientes(self, value):
        ids = []
        for v in value:
            pk = v['ingrediente'].pk
            if pk in ids:
                raise serializers.ValidationError("Hay ingredientes duplicados en la lista.")
            ids.append(pk)
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredientes_data = validated_data.pop('ingredientes', [])
        receta = Receta.objects.create(**validated_data)

        detalles = [
            DetalleIngredientes(receta=receta, ingrediente=item['ingrediente'], cantidad=item['cantidad'])
            for item in ingredientes_data
        ]
        if detalles:
            DetalleIngredientes.objects.bulk_create(detalles)

        return receta

# ─────────────────────────────────────────────────────────────
# Editar/Sincronizar Receta con ingredientes
# ─────────────────────────────────────────────────────────────
class EditarRecetaConIngredientesSerializer(serializers.ModelSerializer):
    ingredientes = DetalleIngredienteInputSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Receta
        fields = ['id','nombre_receta','descripcion','porcentaje_alcohol','contenido_neto','imagen','ingredientes']
        read_only_fields = ['id']
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True},
            'porcentaje_alcohol': {'required': False, 'allow_null': True},
            'contenido_neto': {'required': False, 'allow_null': True},
        }

    def validate_ingredientes(self, value):
        ids = []
        for v in value:
            pk = v['ingrediente'].pk
            if pk in ids:
                raise serializers.ValidationError("Hay ingredientes duplicados en la lista.")
            ids.append(pk)
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredientes_data = validated_data.pop('ingredientes', None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if ingredientes_data is not None:
            actuales = {
                di.ingrediente_id: di
                for di in DetalleIngredientes.objects.filter(receta=instance)
            }

            enviados_ids = set()

            # upsert
            nuevos = []
            for item in ingredientes_data:
                ing = item['ingrediente']
                cant = item['cantidad']
                enviados_ids.add(ing.id)

                if ing.id in actuales:
                    di = actuales[ing.id]
                    if di.cantidad != cant:
                        di.cantidad = cant
                        di.save(update_fields=['cantidad'])
                else:
                    nuevos.append(DetalleIngredientes(receta=instance, ingrediente=ing, cantidad=cant))

            if nuevos:
                DetalleIngredientes.objects.bulk_create(nuevos)

            # delete faltantes
            a_eliminar = set(actuales.keys()) - enviados_ids
            if a_eliminar:
                DetalleIngredientes.objects.filter(receta=instance, ingrediente_id__in=a_eliminar).delete()

        return instance
