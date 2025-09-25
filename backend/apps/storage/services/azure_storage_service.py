# apps/storage/services/azure_storage_service.py
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from django.conf import settings
from django.core.files.base import ContentFile

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure SDK not available. Install with: pip install azure-storage-blob azure-identity")

logger = logging.getLogger(__name__)

class AzureStorageService:
    def __init__(self):
        self.account_name = getattr(settings, 'AZURE_STORAGE_ACCOUNT_NAME', None)
        self.account_key = getattr(settings, 'AZURE_STORAGE_ACCOUNT_KEY', None)
        self.container_name = getattr(settings, 'AZURE_STORAGE_CONTAINER_NAME', 'azure-reports')
        
        # Log de configuración - SIN EMOJIS
        logger.info(f"Configurando Azure Storage:")
        logger.info(f"   Account: {self.account_name}")
        logger.info(f"   Container: {self.container_name}")
        logger.info(f"   Key: {'Configurado' if self.account_key else 'No configurado'}")
        
        if not AZURE_AVAILABLE:
            logger.warning("Azure SDK no disponible. Instalar con: pip install azure-storage-blob azure-identity")
            self.blob_service_client = None
            return
            
        # Inicializar cliente
        if self.account_name and self.account_key:
            try:
                connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                logger.info("Cliente de Azure Storage inicializado exitosamente")
            except Exception as e:
                logger.error(f"Error inicializando cliente de Azure Storage: {str(e)}")
                self.blob_service_client = None
        else:
            logger.warning("Credenciales de Azure Storage no configuradas")
            self.blob_service_client = None


    def is_configured(self) -> bool:
        """Verificar si Azure Storage está configurado"""
        return AZURE_AVAILABLE and self.blob_service_client is not None

    def upload_file(self, file_content: bytes, file_name: str, content_type: str = None) -> Optional[str]:
        """
        Subir archivo a Azure Blob Storage
        
        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            content_type: Tipo MIME del archivo
            
        Returns:
            URL del archivo subido o None si hay error
        """
        if not self.is_configured():
            logger.warning("Azure Storage no configurado. Archivo no subido.")
            return None
            
        try:
            # Crear nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_name = f"{timestamp}_{file_name}"
            
            # Obtener cliente del contenedor
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Crear contenedor si no existe
            try:
                container_client.create_container()
            except Exception:
                pass  # El contenedor ya existe
            
            # Subir archivo
            blob_client = container_client.get_blob_client(unique_name)
            
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings={
                    'content_type': content_type or 'application/octet-stream'
                }
            )
            
            # Retornar URL del archivo
            blob_url = blob_client.url
            logger.info(f"Archivo subido exitosamente: {unique_name}")
            return blob_url
            
        except AzureError as e:
            logger.error(f"Error subiendo archivo a Azure Storage: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado subiendo archivo: {str(e)}")
            return None

    def download_file(self, file_name: str) -> Optional[bytes]:
        """
        Descargar archivo de Azure Blob Storage
        
        Args:
            file_name: Nombre del archivo a descargar
            
        Returns:
            Contenido del archivo en bytes o None si hay error
        """
        if not self.is_configured():
            logger.warning("Azure Storage no configurado")
            return None
            
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            download_stream = blob_client.download_blob()
            return download_stream.readall()
            
        except AzureError as e:
            logger.error(f"Error descargando archivo: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado descargando archivo: {str(e)}")
            return None

    def delete_file(self, file_name: str) -> bool:
        """
        Eliminar archivo de Azure Blob Storage
        
        Args:
            file_name: Nombre del archivo a eliminar
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if not self.is_configured():
            logger.warning("Azure Storage no configurado")
            return False
            
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            blob_client.delete_blob()
            logger.info(f"Archivo eliminado exitosamente: {file_name}")
            return True
            
        except AzureError as e:
            logger.error(f"Error eliminando archivo: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado eliminando archivo: {str(e)}")
            return False

    def list_files(self, prefix: str = "") -> List[Dict]:
        """
        Listar archivos en Azure Blob Storage
        
        Args:
            prefix: Prefijo para filtrar archivos
            
        Returns:
            Lista de diccionarios con información de archivos
        """
        if not self.is_configured():
            logger.warning("Azure Storage no configurado")
            return []
            
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            file_list = []
            for blob in blobs:
                file_info = {
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified,
                    'content_type': blob.content_settings.content_type if blob.content_settings else None,
                    'url': f"{container_client.url}/{blob.name}"
                }
                file_list.append(file_info)
            
            return file_list
            
        except AzureError as e:
            logger.error(f"Error listando archivos: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado listando archivos: {str(e)}")
            return []

    def get_file_url(self, file_name: str, expiry_hours: int = 24) -> Optional[str]:
        """
        Obtener URL con SAS token para acceso temporal
        
        Args:
            file_name: Nombre del archivo
            expiry_hours: Horas de validez del token
            
        Returns:
            URL con SAS token o None si hay error
        """
        if not self.is_configured():
            logger.warning("Azure Storage no configurado")
            return None
            
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            
            # Generar SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=file_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            # Construir URL completa
            blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}?{sas_token}"
            return blob_url
            
        except Exception as e:
            logger.error(f"Error generando URL con SAS token: {str(e)}")
            return None

    def upload_csv_file(self, file_content: bytes, original_filename: str) -> Optional[str]:
        """
        Subir archivo CSV específicamente
        
        Args:
            file_content: Contenido del archivo CSV
            original_filename: Nombre original del archivo
            
        Returns:
            URL del archivo subido
        """
        return self.upload_file(
            file_content=file_content,
            file_name=f"csv/{original_filename}",
            content_type="text/csv"
        )

    def upload_pdf_report(self, pdf_content: bytes, report_name: str) -> Optional[str]:
        """
        Subir reporte PDF específicamente
        
        Args:
            pdf_content: Contenido del PDF
            report_name: Nombre del reporte
            
        Returns:
            URL del reporte subido
        """
        pdf_filename = f"{report_name}.pdf" if not report_name.endswith('.pdf') else report_name
        
        return self.upload_file(
            file_content=pdf_content,
            file_name=f"reports/{pdf_filename}",
            content_type="application/pdf"
        )


# Instancia global del servicio
azure_storage = AzureStorageService()


# Funciones de conveniencia
def upload_file_to_azure(file_content: bytes, file_name: str, content_type: str = None) -> Optional[str]:
    """Función de conveniencia para subir archivos"""
    return azure_storage.upload_file(file_content, file_name, content_type)


def get_azure_file_url(file_name: str, expiry_hours: int = 24) -> Optional[str]:
    """Función de conveniencia para obtener URLs"""
    return azure_storage.get_file_url(file_name, expiry_hours)