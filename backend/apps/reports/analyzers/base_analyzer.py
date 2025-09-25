# apps/reports/analyzers/base_analyzer.py
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    """
    Clase base para analizadores de datos
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Inicializar el analizador con un DataFrame
        
        Args:
            data (pd.DataFrame): Los datos a analizar
        """
        self.df = data.copy() if not data.empty else pd.DataFrame()
        self.insights = {}
    
    def analyze(self) -> Dict[str, Any]:
        """
        Método base para realizar análisis
        Debe ser implementado por las clases hijas
        """
        raise NotImplementedError("El método analyze() debe ser implementado por las clases hijas")
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Obtener los insights generados
        
        Returns:
            Dict[str, Any]: Los insights del análisis
        """
        return self.insights
    
    def _validate_data(self) -> bool:
        """
        Validar que los datos estén en buen estado
        
        Returns:
            bool: True si los datos son válidos
        """
        if self.df.empty:
            logger.warning("DataFrame está vacío")
            return False
        
        if len(self.df.columns) == 0:
            logger.warning("DataFrame no tiene columnas")
            return False
            
        return True