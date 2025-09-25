# apps/reports/utils/cache_manager.py
from django.core.cache import cache
from django.conf import settings
import hashlib
import json

class ReportCacheManager:
    """Gestor de caché para reportes HTML"""
    
    CACHE_PREFIX = 'azure_report_html'
    CACHE_TIMEOUT = getattr(settings, 'REPORT_CACHE_TIMEOUT', 3600)  # 1 hora
    
    @classmethod
    def get_cache_key(cls, report_id, csv_hash=None):
        """Genera clave de caché única"""
        key_data = f"{report_id}_{csv_hash or 'no_csv'}"
        return f"{cls.CACHE_PREFIX}_{hashlib.md5(key_data.encode()).hexdigest()}"
    
    @classmethod
    def get_csv_hash(cls, csv_file_path):
        """Calcula hash del archivo CSV"""
        try:
            import hashlib
            with open(csv_file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (FileNotFoundError, OSError):
            return None
    
    @classmethod
    def get_cached_html(cls, report):
        """Obtiene HTML del caché si existe"""
        csv_hash = None
        if report.get_csv_file_path():
            csv_hash = cls.get_csv_hash(report.get_csv_file_path())
        
        cache_key = cls.get_cache_key(report.id, csv_hash)
        return cache.get(cache_key)
    
    @classmethod
    def cache_html(cls, report, html_content):
        """Guarda HTML en caché"""
        csv_hash = None
        if report.get_csv_file_path():
            csv_hash = cls.get_csv_hash(report.get_csv_file_path())
        
        cache_key = cls.get_cache_key(report.id, csv_hash)
        cache.set(cache_key, html_content, cls.CACHE_TIMEOUT)
        return cache_key
    
    @classmethod
    def invalidate_cache(cls, report):
        """Invalida caché del reporte"""
        # Eliminar múltiples versiones posibles
        for csv_hash in [None, cls.get_csv_hash(report.get_csv_file_path())]:
            cache_key = cls.get_cache_key(report.id, csv_hash)
            cache.delete(cache_key)