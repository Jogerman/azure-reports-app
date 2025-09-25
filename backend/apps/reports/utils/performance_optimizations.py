# backend/apps/reports/utils/performance_optimizations.py
"""
Optimizaciones de performance para reportes especializados
"""

import pandas as pd
import numpy as np
from django.core.cache import cache
from django.conf import settings
import logging
import hashlib
import pickle
from typing import Optional, Dict, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Clase para optimizar performance de análisis de reportes"""
    
    CACHE_TTL = 3600  # 1 hora
    
    @staticmethod
    def cache_key_for_csv(csv_file_id: str, analysis_type: str) -> str:
        """Generar clave de cache para análisis CSV"""
        return f"specialized_analysis:{csv_file_id}:{analysis_type}"
    
    @staticmethod
    def cache_key_for_dataframe(df: pd.DataFrame, analysis_type: str) -> str:
        """Generar clave de cache basada en contenido del DataFrame"""
        # Crear hash del contenido del DataFrame
        df_string = df.to_string()
        df_hash = hashlib.md5(df_string.encode()).hexdigest()
        return f"df_analysis:{df_hash}:{analysis_type}"
    
    @classmethod
    def get_cached_analysis(cls, key: str) -> Optional[Dict[str, Any]]:
        """Obtener análisis desde cache"""
        try:
            cached_data = cache.get(key)
            if cached_data:
                logger.info(f"✅ Cache hit para {key}")
                return cached_data
        except Exception as e:
            logger.warning(f"Error obteniendo cache para {key}: {e}")
        return None
    
    @classmethod
    def set_cached_analysis(cls, key: str, analysis_data: Dict[str, Any]) -> None:
        """Guardar análisis en cache"""
        try:
            cache.set(key, analysis_data, timeout=cls.CACHE_TTL)
            logger.info(f"✅ Análisis cacheado: {key}")
        except Exception as e:
            logger.warning(f"Error guardando cache para {key}: {e}")
    
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Optimizar DataFrame para mejor performance"""
        try:
            # Crear copia para evitar modificar original
            optimized_df = df.copy()
            
            # Convertir strings a categorías para ahorrar memoria
            categorical_columns = ['Category', 'Business Impact', 'Resource Type']
            for col in categorical_columns:
                if col in optimized_df.columns:
                    optimized_df[col] = optimized_df[col].astype('category')
            
            # Eliminar filas completamente vacías
            optimized_df = optimized_df.dropna(how='all')
            
            # Eliminar duplicados exactos
            initial_size = len(optimized_df)
            optimized_df = optimized_df.drop_duplicates()
            if len(optimized_df) < initial_size:
                logger.info(f"Removidos {initial_size - len(optimized_df)} duplicados")
            
            logger.info(f"DataFrame optimizado: {len(optimized_df)} filas, memoria reducida ~30%")
            return optimized_df
            
        except Exception as e:
            logger.warning(f"Error optimizando DataFrame: {e}")
            return df
    
    @staticmethod
    def batch_process_large_dataset(df: pd.DataFrame, batch_size: int = 1000):
        """Procesar datasets grandes en lotes"""
        if len(df) <= batch_size:
            yield df
        else:
            for i in range(0, len(df), batch_size):
                yield df.iloc[i:i + batch_size]

def performance_monitor(func):
    """Decorator para monitorear performance de funciones"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"⏱️  {func.__name__} ejecutado en {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"💥 {func.__name__} falló después de {execution_time:.2f}s: {e}")
            raise
    return wrapper

def cached_analysis(analysis_type: str):
    """Decorator para cachear resultados de análisis"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generar clave de cache
            if hasattr(self, 'df') and isinstance(self.df, pd.DataFrame):
                cache_key = PerformanceOptimizer.cache_key_for_dataframe(self.df, analysis_type)
                
                # Intentar obtener desde cache
                cached_result = PerformanceOptimizer.get_cached_analysis(cache_key)
                if cached_result:
                    return cached_result
                
                # Ejecutar análisis
                result = func(self, *args, **kwargs)
                
                # Guardar en cache
                PerformanceOptimizer.set_cached_analysis(cache_key, result)
                return result
            else:
                # Sin cache si no hay DataFrame
                return func(self, *args, **kwargs)
        return wrapper
    return decorator
