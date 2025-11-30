"""
Serializers para la API REST de incidencias.
"""

from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Incident, IncidentAttachment, IncidentEvent


class IncidentAttachmentSerializer(serializers.ModelSerializer):
    """Serializer para adjuntos de incidentes"""
    
    class Meta:
        model = IncidentAttachment
        fields = ['id', 'file_url', 'mime_type', 'size_bytes', 'created_at']
        read_only_fields = ['id', 'created_at']


class IncidentEventSerializer(serializers.ModelSerializer):
    """Serializer para eventos/historial de incidentes"""
    
    class Meta:
        model = IncidentEvent
        fields = ['id', 'event_type', 'payload', 'created_at']
        read_only_fields = ['id', 'created_at']


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer principal para incidentes"""
    
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    # Campos con nombres en español para compatibilidad con frontend
    tipo = serializers.CharField(source='incident_type', required=False)
    descripcion = serializers.CharField(source='description', required=False)
    estado = serializers.CharField(source='status', required=False)
    direccion = serializers.CharField(source='address', required=False)
    ubicacion = serializers.SerializerMethodField()
    
    # Campos calculados para lectura
    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'reporter_kind', 'reporter_id', 
            'tipo', 'descripcion', 'estado', 'direccion',
            'latitude', 'longitude', 'lat', 'lon',
            'ubicacion', 'photo_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reporter_id', 'created_at', 'updated_at']
    
    def get_ubicacion(self, obj):
        """Retorna ubicación en formato GeoJSON"""
        if obj.location:
            return {
                'type': 'Point',
                'coordinates': [obj.location.x, obj.location.y]
            }
        return None
    
    def get_lat(self, obj):
        """Retorna latitud del punto"""
        if obj.location:
            return obj.location.y
        return None
    
    def get_lon(self, obj):
        """Retorna longitud del punto"""
        if obj.location:
            return obj.location.x
        return None
    
    def create(self, validated_data):
        """Crea un incidente con ubicación geográfica"""
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # Crear Point de PostGIS
        validated_data['location'] = Point(longitude, latitude)
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Actualiza un incidente"""
        if 'latitude' in validated_data and 'longitude' in validated_data:
            latitude = validated_data.pop('latitude')
            longitude = validated_data.pop('longitude')
            validated_data['location'] = Point(longitude, latitude)
        
        return super().update(instance, validated_data)


class IncidentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear incidentes desde app móvil y frontend.
    Acepta campos en español para compatibilidad.
    """
    
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    
    # Campos en español
    tipo = serializers.CharField(source='incident_type', required=False)
    descripcion = serializers.CharField(source='description', required=False)
    direccion = serializers.CharField(source='address', required=False)
    ubicacion = serializers.DictField(required=False, write_only=True)
    
    photo_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text='URL de foto/evidencia inicial'
    )
    
    class Meta:
        model = Incident
        fields = [
            'tipo', 'descripcion', 'direccion',
            'latitude', 'longitude', 'ubicacion',
            'photo_url', 'reporter_kind'
        ]
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Si viene ubicacion como objeto GeoJSON, extraer coordenadas
        if 'ubicacion' in data:
            coords = data['ubicacion'].get('coordinates', [])
            if len(coords) == 2:
                data['longitude'] = coords[0]
                data['latitude'] = coords[1]
        
        # Validar rango de coordenadas si están presentes
        if 'latitude' in data and data['latitude'] is not None:
            if not (-90 <= data['latitude'] <= 90):
                raise serializers.ValidationError({
                    'latitude': 'Debe estar entre -90 y 90'
                })
        if 'longitude' in data and data['longitude'] is not None:
            if not (-180 <= data['longitude'] <= 180):
                raise serializers.ValidationError({
                    'longitude': 'Debe estar entre -180 y 180'
                })
        
        return data
    
    def create(self, validated_data):
        """Crea incidente con ubicación y foto inicial"""
        # Remover ubicacion si existe (ya procesada en validate)
        validated_data.pop('ubicacion', None)
        
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        photo_url = validated_data.pop('photo_url', None)
        
        # Crear punto geográfico si hay coordenadas
        if latitude and longitude:
            validated_data['location'] = Point(longitude, latitude)
        
        # Configurar valores por defecto
        if 'reporter_kind' not in validated_data:
            validated_data['reporter_kind'] = 'ciudadano'
        if 'status' not in validated_data:
            validated_data['status'] = 'REPORTADA'
        
        # Guardar photo_url si existe
        if photo_url:
            validated_data['photo_url'] = photo_url
        
        # Obtener reporter_id del usuario actual (si está autenticado)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['reporter_id'] = request.user.id
        
        # Crear incidente
        incident = Incident.objects.create(**validated_data)
        
        # Si hay foto inicial, crear adjunto
        if photo_url:
            IncidentAttachment.objects.create(
                incident=incident,
                file_url=photo_url,
                mime_type='image/jpeg'
            )
            incident.photos_count = 1
            incident.save()
        
        return incident


class IncidentUpdateStatusSerializer(serializers.Serializer):
    """Serializer para actualizar el estado de un incidente"""
    
    status = serializers.ChoiceField(
        choices=Incident._meta.get_field('status').choices,
        help_text='Nuevo estado del incidente'
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Notas adicionales sobre el cambio'
    )


class IncidentValidationSerializer(serializers.Serializer):
    """Serializer para validar/rechazar incidentes por administradores"""
    
    action = serializers.ChoiceField(
        choices=['validate', 'reject'],
        help_text='Acción a realizar: validate o reject'
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Notas/razón de la decisión'
    )
