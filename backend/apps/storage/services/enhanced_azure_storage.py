# backend/apps/storage/services/enhanced_azure_storage.py
import os
import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
import io
import gzip
import base64

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure SDK not available. Install with: pip install azure-storage-blob azure-identity")

logger = logging.getLogger(__name__)

class EnhancedAzureStorageService:
    """Servicio Azure Storage mejorado para PDFs, DataFrames y archivos del sistema"""
    
    def __init__(self):
        self.account_name = getattr(settings, 'AZURE_STORAGE_ACCOUNT_NAME', None)
        self.account_key = getattr(settings, 'AZURE_STORAGE_ACCOUNT_KEY', None)
        self.container_name = getattr(settings, 'AZURE_STORAGE_CONTAINER_NAME', 'azure-reports')
        
        # Contenedores específicos por tipo
        self.containers = {
            'pdfs': f"{self.container_name}-pdfs",
            'data': f"{self.container_name}-data", 
            'csvs': f"{self.container_name}-csvs",
            'cache': f"{self.container_name}-cache"
        }
        
        self.blob_service_client = None
        
        if AZURE_AVAILABLE and self.account_name and self.account_key:
            try:
                connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                
                # Crear contenedores si no existen
                self._ensure_containers_exist()
                logger.info("✅ Enhanced Azure Storage Service inicializado")
                
            except Exception as e:
                logger.error(f"❌ Error inicializando Azure Storage: {e}")
                self.blob_service_client = None
        else:
            logger.warning("⚠️ Azure Storage no configurado completamente")

    def _ensure_containers_exist(self):
        """Crear contenedores necesarios si no existen"""
        if not self.is_available():
            return
            
        for container_type, container_name in self.containers.items():
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                container_client.create_container()
                logger.info(f"Contenedor creado: {container_name}")
            except Exception:
                # El contenedor ya existe
                pass

    def is_available(self) -> bool:
        """Verificar si Azure Storage está disponible"""
        return AZURE_AVAILABLE and self.blob_service_client is not None

    # =============================================
    # MÉTODOS PARA PDFs
    # =============================================
    
    def upload_pdf(self, pdf_bytes: bytes, report_id: str, client_name: str = "client") -> Optional[Dict[str, str]]:
        """
        Subir PDF de reporte a Azure Storage - VERSIÓN CORREGIDA
        """
        if not self.is_available():
            logger.warning("Azure Storage no disponible para subir PDF")
            return None
            
        try:
            # Crear nombre único para el PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_client_name = self._sanitize_filename(client_name)
            blob_name = f"reports/{safe_client_name}/{report_id}_{timestamp}.pdf"
            
            # Subir PDF - CORRECCIÓN: usar ContentSettings correctamente
            from azure.storage.blob import ContentSettings
            
            container_client = self.blob_service_client.get_container_client(self.containers['pdfs'])
            blob_client = container_client.get_blob_client(blob_name)
            
            # CORRECCIÓN: Crear ContentSettings apropiadamente
            content_settings = ContentSettings(
                content_type='application/pdf',
                content_disposition=f'inline; filename="azure_advisor_{safe_client_name}.pdf"'
            )
            
            blob_client.upload_blob(
                pdf_bytes,
                overwrite=True,
                content_settings=content_settings,  # <- CORREGIDO
                metadata={
                    'report_id': str(report_id),
                    'client_name': client_name,
                    'generated_at': datetime.now().isoformat(),
                    'file_type': 'azure_advisor_pdf'
                }
            )
            
            # Generar URL con SAS token para acceso
            pdf_url = self._generate_sas_url(self.containers['pdfs'], blob_name, hours=24*30)  # 30 días
            
            result = {
                'blob_name': blob_name,
                'blob_url': pdf_url,
                'public_url': blob_client.url,
                'container': self.containers['pdfs'],
                'size_bytes': len(pdf_bytes),
                'uploaded_at': timezone.now().isoformat()
            }
            
            logger.info(f"✅ PDF subido exitosamente: {blob_name} ({len(pdf_bytes)} bytes)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error subiendo PDF: {e}")
            return None
    # =============================================
    # MÉTODOS PARA DATAFRAMES
    # =============================================
    
    def upload_dataframe(self, df: pd.DataFrame, csv_file_id: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, str]]:
        """
        Subir DataFrame como datos raw en múltiples formatos - VERSIÓN CORREGIDA
        """
        if not self.is_available():
            logger.warning("Azure Storage no disponible para subir DataFrame")
            return None
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_path = f"dataframes/{csv_file_id}/{timestamp}"
            
            uploaded_files = {}
            
            # CORRECCIÓN: Importar ContentSettings
            from azure.storage.blob import ContentSettings
            
            # 1. Guardar como CSV comprimido (para lectura rápida)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_compressed = gzip.compress(csv_buffer.getvalue().encode('utf-8'))
            
            csv_blob_name = f"{base_path}/data.csv.gz"
            csv_url = self._upload_blob_fixed(
                self.containers['data'], 
                csv_blob_name, 
                csv_compressed,
                content_type='application/gzip',
                metadata_dict={
                    'csv_file_id': str(csv_file_id),
                    'format': 'csv_compressed',
                    'rows': str(len(df)),
                    'columns': str(len(df.columns)),
                    'generated_at': datetime.now().isoformat()
                }
            )
            
            if csv_url:
                uploaded_files['csv_compressed'] = {
                    'blob_name': csv_blob_name,
                    'url': csv_url,
                    'format': 'csv.gz',
                    'size_bytes': len(csv_compressed)
                }
            
            # 2. Guardar como JSON (para compatibilidad con frontend)
            json_data = {
                'metadata': {
                    'csv_file_id': str(csv_file_id),
                    'rows_count': len(df),
                    'columns_count': len(df.columns),
                    'columns': list(df.columns),
                    'generated_at': datetime.now().isoformat(),
                    'data_types': df.dtypes.astype(str).to_dict(),
                    **(metadata or {})
                },
                'data': df.to_dict('records')
            }
            
            # CORRECCIÓN: Remover ensure_ascii que no existe en pandas más nuevos
            json_compressed = gzip.compress(json.dumps(json_data, default=str).encode('utf-8'))
            json_blob_name = f"{base_path}/data.json.gz"
            
            json_url = self._upload_blob_fixed(
                self.containers['data'],
                json_blob_name,
                json_compressed,
                content_type='application/json',
                metadata_dict={
                    'csv_file_id': str(csv_file_id),
                    'format': 'json_compressed',
                    'rows': str(len(df)),
                    'columns': str(len(df.columns))
                }
            )
            
            if json_url:
                uploaded_files['json_compressed'] = {
                    'blob_name': json_blob_name,
                    'url': json_url,
                    'format': 'json.gz',
                    'size_bytes': len(json_compressed)
                }
            
            # 3. Guardar muestra pequeña sin comprimir (para vista rápida)
            sample_df = df.head(100)  # Primeras 100 filas
            # CORRECCIÓN: Usar json.dumps en lugar de to_json con parámetros no válidos
            sample_json = json.dumps(sample_df.to_dict('records'), default=str)
            sample_blob_name = f"{base_path}/sample.json"
            
            sample_url = self._upload_blob_fixed(
                self.containers['data'],
                sample_blob_name,
                sample_json.encode('utf-8'),
                content_type='application/json',
                metadata_dict={
                    'csv_file_id': str(csv_file_id),
                    'format': 'sample_json',
                    'is_sample': 'true',
                    'sample_size': str(len(sample_df))
                }
            )
            
            if sample_url:
                uploaded_files['sample'] = {
                    'blob_name': sample_blob_name,
                    'url': sample_url,
                    'format': 'json',
                    'size_bytes': len(sample_json.encode('utf-8'))
                }
            
            logger.info(f"✅ DataFrame subido en {len(uploaded_files)} formatos para CSV {csv_file_id}")
            return {
                'base_path': base_path,
                'files': uploaded_files,
                'primary_url': uploaded_files.get('csv_compressed', {}).get('url'),
                'sample_url': uploaded_files.get('sample', {}).get('url'),
                'metadata': {
                    'rows_count': len(df),
                    'columns_count': len(df.columns),
                    'uploaded_at': timestamp
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo DataFrame: {e}")
            return None

    # =============================================
    # MÉTODOS PARA DESCARGAR DATOS
    # =============================================
    
    def download_dataframe(self, csv_file_id: str, format_type: str = 'csv_compressed') -> Optional[pd.DataFrame]:
        """
        Descargar DataFrame desde Azure Storage
        
        Args:
            csv_file_id: ID del archivo CSV
            format_type: Tipo de formato ('csv_compressed', 'json_compressed', 'sample')
            
        Returns:
            DataFrame o None si hay error
        """
        if not self.is_available():
            logger.warning("Azure Storage no disponible para descargar DataFrame")
            return None
            
        try:
            # Buscar el archivo más reciente para este CSV
            container_client = self.blob_service_client.get_container_client(self.containers['data'])
            
            # Listar blobs con el prefijo correcto
            prefix = f"dataframes/{csv_file_id}/"
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            # Encontrar el blob más reciente del formato solicitado
            target_blob = None
            latest_time = None
            
            for blob in blobs:
                if format_type == 'csv_compressed' and blob.name.endswith('data.csv.gz'):
                    blob_time = blob.last_modified
                    if latest_time is None or blob_time > latest_time:
                        latest_time = blob_time
                        target_blob = blob.name
                elif format_type == 'json_compressed' and blob.name.endswith('data.json.gz'):
                    blob_time = blob.last_modified
                    if latest_time is None or blob_time > latest_time:
                        latest_time = blob_time
                        target_blob = blob.name
                elif format_type == 'sample' and blob.name.endswith('sample.json'):
                    blob_time = blob.last_modified
                    if latest_time is None or blob_time > latest_time:
                        latest_time = blob_time
                        target_blob = blob.name
            
            if not target_blob:
                logger.warning(f"No se encontró DataFrame para CSV {csv_file_id} formato {format_type}")
                return None
            
            # Descargar el blob
            blob_client = container_client.get_blob_client(target_blob)
            blob_data = blob_client.download_blob().readall()
            
            # Procesar según el formato
            if format_type == 'csv_compressed':
                decompressed_data = gzip.decompress(blob_data).decode('utf-8')
                df = pd.read_csv(io.StringIO(decompressed_data))
                
            elif format_type == 'json_compressed':
                decompressed_data = gzip.decompress(blob_data).decode('utf-8')
                json_data = json.loads(decompressed_data)
                df = pd.DataFrame(json_data['data'])
                
            elif format_type == 'sample':
                json_data = json.loads(blob_data.decode('utf-8'))
                df = pd.DataFrame(json_data)
                
            else:
                raise ValueError(f"Formato no soportado: {format_type}")
            
            logger.info(f"✅ DataFrame descargado: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error descargando DataFrame: {e}")
            return None

    # =============================================
    # MÉTODOS AUXILIARES
    # =============================================
    
    def _upload_blob(self, container_name: str, blob_name: str, data: bytes, content_type: str = None, metadata: Dict[str, str] = None) -> Optional[str]:
        """Método auxiliar para subir blob - VERSIÓN CORREGIDA"""
        return self._upload_blob_fixed(container_name, blob_name, data, content_type, metadata)
    
    def _upload_blob_fixed(self, container_name: str, blob_name: str, data: bytes, content_type: str = None, metadata_dict: Dict[str, str] = None) -> Optional[str]:
        """Método auxiliar corregido para subir blob"""
        try:
            # CORRECCIÓN: Usar ContentSettings apropiadamente
            from azure.storage.blob import ContentSettings
            
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            # Crear ContentSettings si se especifica content_type
            content_settings = None
            if content_type:
                content_settings = ContentSettings(content_type=content_type)
            
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=content_settings,
                metadata=metadata_dict
            )
            
            # Retornar URL con SAS token
            return self._generate_sas_url(container_name, blob_name)
            
        except Exception as e:
            logger.error(f"Error subiendo blob {blob_name}: {e}")
            return None

    def _generate_sas_url(self, container_name: str, blob_name: str, hours: int = 24) -> Optional[str]:
        """Generar URL con SAS token"""
        try:
            if not self.account_key:
                return None
                
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                account_key=self.account_key,
                container_name=container_name,
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=hours)
            )
            
            return f"https://{self.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
            
        except Exception as e:
            logger.error(f"Error generando SAS URL: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitizar nombre de archivo para Azure"""
        import re
        # Remover caracteres no válidos
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', str(filename))
        # Limitar longitud
        return sanitized[:50].strip()

    def get_storage_info(self) -> Dict[str, Any]:
        """Obtener información del estado del storage"""
        if not self.is_available():
            return {
                'status': 'unavailable',
                'reason': 'Azure Storage not configured or available'
            }
        
        try:
            info = {
                'status': 'available',
                'account_name': self.account_name,
                'containers': self.containers,
                'timestamp': datetime.now().isoformat()
            }
            
            # Obtener estadísticas de contenedores
            container_stats = {}
            for container_type, container_name in self.containers.items():
                try:
                    container_client = self.blob_service_client.get_container_client(container_name)
                    blobs = list(container_client.list_blobs())
                    container_stats[container_type] = {
                        'blob_count': len(blobs),
                        'total_size': sum(blob.size for blob in blobs if blob.size)
                    }
                except Exception:
                    container_stats[container_type] = {'error': 'Unable to access'}
            
            info['container_stats'] = container_stats
            return info
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Instancia global del servicio mejorado
enhanced_azure_storage = EnhancedAzureStorageService()