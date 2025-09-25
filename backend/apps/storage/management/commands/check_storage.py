# apps/storage/management/commands/check_storage.py
from django.core.management.base import BaseCommand
from apps.storage.services.azure_storage_service import AzureStorageService

class Command(BaseCommand):
    help = 'Verificar configuración de Azure Storage'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Verificando Azure Storage...")
        
        storage = AzureStorageService()
        
        if storage.is_configured():
            self.stdout.write(self.style.SUCCESS("✅ Azure Storage configurado correctamente"))
            
            try:
                files = storage.list_files()
                self.stdout.write(f"📁 Archivos encontrados: {len(files)}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error listando archivos: {str(e)}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Azure Storage no configurado"))
            self.stdout.write("💡 Configura las variables AZURE_STORAGE_ACCOUNT_NAME y AZURE_STORAGE_ACCOUNT_KEY")
