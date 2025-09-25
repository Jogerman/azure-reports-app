# apps/reports/serializers.py
from rest_framework import serializers
from .models import CSVFile, Report
import logging

logger = logging.getLogger(__name__)

class CSVFileSerializer(serializers.ModelSerializer):
    """Serializer para archivos CSV"""
    file_size_mb = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    is_valid_csv = serializers.ReadOnlyField()
    
    class Meta:
        model = CSVFile
        fields = [
            'id', 'original_filename', 'file_size', 'file_size_mb', 
            'content_type', 'file_extension', 'is_valid_csv',
            'processing_status', 'error_message', 'rows_count', 
            'columns_count', 'upload_date', 'processed_date',
            'azure_blob_url'
        ]
        read_only_fields = [
            'id', 'upload_date', 'processed_date', 'file_size_mb',
            'file_extension', 'is_valid_csv', 'azure_blob_url'
        ]

class CSVFileUploadSerializer(serializers.ModelSerializer):
    """Serializer específico para upload de CSV"""
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = CSVFile
        fields = ['file']
    
    def validate_file(self, value):
        """Validar archivo CSV"""
        # Verificar extensión
        if not value.name.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise serializers.ValidationError(
                "Solo se permiten archivos CSV, XLS o XLSX"
            )
        
        # Verificar tamaño (50MB máximo)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError(
                "El archivo no puede ser mayor a 50MB"
            )
        
        return value
    
    def create(self, validated_data):
        """Crear instancia y procesar archivo"""
        file = validated_data.pop('file')
        user = self.context['request'].user
        
        try:
            # Crear instancia del CSV
            csv_file = CSVFile.objects.create(
                user=user,
                original_filename=file.name,
                file_size=file.size,
                content_type=file.content_type if hasattr(file, 'content_type') else 'text/csv',
                processing_status='pending'
            )
            
            # Guardar el archivo temporalmente y obtener su path
            # NO pasamos el objeto InMemoryUploadedFile directamente a Celery
            import tempfile
            import os
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                # Escribir el contenido del archivo
                for chunk in file.chunks():
                    tmp_file.write(chunk)
                temp_file_path = tmp_file.name
            
            # Procesar archivo de forma asíncrona con el path del archivo temporal
            from .tasks import process_csv_file
            process_csv_file.delay(csv_file.id, temp_file_path)
            
            logger.info(f"CSV file {csv_file.id} created and queued for processing")
            
            return csv_file
            
        except Exception as e:
            logger.error(f"Error creating CSV file: {str(e)}")
            # Si algo falla, asegurarnos de limpiar
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise serializers.ValidationError(f"Error procesando archivo: {str(e)}")

class ReportSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    csv_file_details = CSVFileSerializer(source='csv_file', read_only=True)
    processing_time = serializers.SerializerMethodField()
    has_content = serializers.SerializerMethodField()
    recommendations_count = serializers.SerializerMethodField()
    potential_savings = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'description', 'report_type', 'status',
            'created_at', 'generated_at', 'user_email', 'csv_file',
            'csv_file_details', 'analysis_data', 'processing_time',  # ✅ Usar analysis_data
            'has_content', 'recommendations_count', 'potential_savings'
        ]
        read_only_fields = [
            'id', 'created_at', 'generated_at', 'user_email',
            'csv_file_details', 'processing_time', 'has_content',
            'recommendations_count', 'potential_savings'
        ]
    
    def get_processing_time(self, obj):
        """Calcular tiempo de procesamiento"""
        if obj.generated_at and obj.created_at:
            delta = obj.generated_at - obj.created_at
            return delta.total_seconds()
        return None
    
    def get_has_content(self, obj):
        """Verificar si el reporte tiene contenido generado"""
        # ✅ ACTUALIZAR para usar analysis_data
        if obj.analysis_data and 'generated_content' in obj.analysis_data:
            return True
        return False
    
    def get_recommendations_count(self, obj):
        """Obtener número de recomendaciones del CSV asociado"""
        try:
            if obj.csv_file and obj.csv_file.analysis_data:
                analysis_data = obj.csv_file.analysis_data
                
                # Buscar en executive_summary
                exec_summary = analysis_data.get('executive_summary', {})
                if 'total_actions' in exec_summary:
                    return exec_summary['total_actions']
                
                # Buscar directamente
                if 'total_recommendations' in analysis_data:
                    return analysis_data['total_recommendations']
                
            return 0
        except:
            return 0
    
    def get_potential_savings(self, obj):
        """Obtener ahorros potenciales del CSV asociado"""
        try:
            if obj.csv_file and obj.csv_file.analysis_data:
                analysis_data = obj.csv_file.analysis_data
                cost_optimization = analysis_data.get('cost_optimization', {})
                estimated_savings = cost_optimization.get('estimated_monthly_optimization', 0)
                return estimated_savings
            return 0
        except:
            return 0

class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes"""
    csv_file_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Report
        fields = [
            'title', 'description', 'report_type', 'csv_file_id'
        ]
    
    def validate_csv_file_id(self, value):
        """Validar que el CSV file existe y pertenece al usuario"""
        if value:
            user = self.context['request'].user
            try:
                csv_file = CSVFile.objects.get(id=value, user=user)
                if csv_file.processing_status != 'completed':
                    raise serializers.ValidationError(
                        "El archivo CSV aún está siendo procesado"
                    )
                return value
            except CSVFile.DoesNotExist:
                raise serializers.ValidationError(
                    "Archivo CSV no encontrado o no tienes permisos"
                )
        return value
    
    def create(self, validated_data):
        """Crear reporte con CSV file si se proporciona"""
        csv_file_id = validated_data.pop('csv_file_id', None)
        csv_file = None
        
        if csv_file_id:
            csv_file = CSVFile.objects.get(id=csv_file_id)
        
        report = Report.objects.create(
            csv_file=csv_file,
            **validated_data
        )
        
        return report