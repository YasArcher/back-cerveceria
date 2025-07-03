from rest_framework import serializers
from .models import Ingrediente, DetalleIngredientes, Receta, TipoIngrediente, UnidadMedida

# ─────────────────────────────────────────────────────────────────────
# 📦 Serializers de modelos base
# ─────────────────────────────────────────────────────────────────────

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = '__all__'

class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = '__all__'

class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = '__all__'

# ─────────────────────────────────────────────────────────────────────
# 📋 Serializers de lógica personalizada (POST, validaciones)
# ─────────────────────────────────────────────────────────────────────

class IngredienteConRecetaSerializer(serializers.ModelSerializer):
    receta = serializers.IntegerField(required=False, write_only=True)  # Campo adicional para vincular al crear

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

        # Verifica si ya existe esa relación
        if DetalleIngredientes.objects.filter(receta=receta, ingrediente=ingrediente).exists():
            raise serializers.ValidationError("Este ingrediente ya está asignado a la receta.")
        return data

# ─────────────────────────────────────────────────────────────────────
# 📘 Serializers para respuestas anidadas o GET personalizados
# ─────────────────────────────────────────────────────────────────────

class IngredienteBasicoSerializer(serializers.ModelSerializer):
    unidad = UnidadSerializer()
    
    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre_ingrediente', 'unidad', 'stock']

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
        ingredientes = Ingrediente.objects.filter(
            tipo=tipo,
            detalleingredientes__receta=receta
        )
        return IngredienteBasicoSerializer(ingredientes, many=True).data

class RecetaConIngredientesSerializer(serializers.ModelSerializer):
    tipos = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = ['id', 'nombre', 'descripcion', 'tipos']

    def get_tipos(self, receta):
        tipos = TipoIngrediente.objects.all()
        return TipoIngredienteConIngredientesDeRecetaSerializer(tipos, many=True, context={'receta': receta}).data


# ─────────────────────────────────────────────────────────────────────
# 🍺 Serializer para preparar una bebida
# ─────────────────────────────────────────────────────────────────────

class PrepararBebidaSerializer(serializers.Serializer):
    receta_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)