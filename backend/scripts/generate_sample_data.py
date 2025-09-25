# backend/scripts/generate_sample_data.py
"""
Script para generar datos de ejemplo para probar reportes especializados
Ejecutar con: python manage.py shell < scripts/generate_sample_data.py
"""

import os
import csv
import random
from datetime import datetime, timedelta

def generate_sample_csv_data():
    """Generar archivos CSV de ejemplo para testing"""
    
    print("📊 Generando datos CSV de ejemplo...")
    
    # Crear directorio de samples si no existe
    samples_dir = 'backend/sample_data'
    os.makedirs(samples_dir, exist_ok=True)
    
    # Generar CSV de seguridad
    generate_security_csv(samples_dir)
    
    # Generar CSV de rendimiento
    generate_performance_csv(samples_dir)
    
    # Generar CSV de costos
    generate_cost_csv(samples_dir)
    
    # Generar CSV completo (mixto)
    generate_comprehensive_csv(samples_dir)
    
    print("✅ Archivos CSV de ejemplo generados en backend/sample_data/")

def generate_security_csv(output_dir):
    """Generar CSV enfocado en seguridad"""
    filename = os.path.join(output_dir, 'sample_security_recommendations.csv')
    
    security_recommendations = [
        'Virtual machines should have encryption at host enabled',
        'TLS should be updated to the latest version for web apps',
        'Machines should be configured to periodically check for missing system updates',
        'Virtual machines and virtual machine scale sets should have encryption at host enabled',
        'Diagnostic logs in App Service should be enabled',
        'Managed identity should be used in web apps',
        'Storage account public access should be disallowed',
        'Guest Configuration extension should be installed on machines',
        'API Management minimum API version should be set to 2019-12-01 or higher',
        'Enable Trusted Launch foundational excellence, and modern security for Existing Generation 2 VMs'
    ]
    
    resource_types = [
        'Virtual machine', 'App service', 'Storage Account', 'Virtual machine',
        'App service', 'App service', 'Storage Account', 'Virtual machine',
        'Api Management', 'Virtual machine'
    ]
    
    business_impacts = ['High', 'Medium', 'High', 'Medium', 'Medium', 'Medium', 'High', 'Medium', 'Medium', 'High']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Week Number', 'Session Number', 'Category', 'Business Impact', 'Recommendation', 'Resource Type'])
        
        for i, (rec, resource, impact) in enumerate(zip(security_recommendations, resource_types, business_impacts), 1):
            writer.writerow([i, 1, random.randint(1, 10), 'Security', impact, rec, resource])
    
    print(f"  ✅ Generado: {filename}")

def generate_performance_csv(output_dir):
    """Generar CSV enfocado en rendimiento"""
    filename = os.path.join(output_dir, 'sample_performance_recommendations.csv')
    
    performance_recommendations = [
        'Right-size or shutdown underutilized virtual machines',
        'Enable autoscale to ensure optimal performance',
        'Upgrade to the latest version of the .NET Framework',
        'Use SSD disks for better IOPS performance',
        'Consider using Azure CDN for global content delivery',
        'Optimize database query performance',
        'Enable connection pooling for better resource utilization',
        'Consider using Azure Cache for Redis for faster data access'
    ]
    
    resource_types = [
        'Virtual machine', 'App service', 'App service', 'Virtual machine',
        'Storage Account', 'Azure SQL Database', 'App service', 'Virtual machine'
    ]
    
    business_impacts = ['High', 'Medium', 'Low', 'High', 'Medium', 'High', 'Medium', 'Medium']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Week Number', 'Session Number', 'Category', 'Business Impact', 'Recommendation', 'Resource Type'])
        
        for i, (rec, resource, impact) in enumerate(zip(performance_recommendations, resource_types, business_impacts), 1):
            writer.writerow([i, 1, random.randint(1, 8), 'Performance', impact, rec, resource])
    
    print(f"  ✅ Generado: {filename}")

def generate_cost_csv(output_dir):
    """Generar CSV enfocado en costos"""
    filename = os.path.join(output_dir, 'sample_cost_recommendations.csv')
    
    cost_recommendations = [
        'Consider virtual machine reserved instance to save over your on-demand costs',
        'Consider App Service reserved instance to save over your pay-as-you-go costs',
        'Consider Azure Synapse Analytics (formerly SQL DW) reserved instance to save over your pay-as-you-go costs',
        'Consider Database for PostgreSQL reserved instance to save over your pay-as-you-go costs',
        'Consider virtual machine reserved instance to save over your on-demand costs',
        'Right-size or shutdown underutilized virtual machines',
        'Consider Database for MySQL reserved instance to save over your pay-as-you-go costs',
        'Delete unattached disks to save on storage costs',
        'Resize virtual machines to optimize costs',
        'Consider using Azure Hybrid Benefit for Windows Server'
    ]
    
    resource_types = [
        'Subscription', 'Subscription', 'Subscription', 'Subscription', 'Subscription',
        'Virtual machine', 'Subscription', 'Storage Account', 'Virtual machine', 'Subscription'
    ]
    
    business_impacts = ['High', 'Medium', 'High', 'Medium', 'High', 'High', 'Medium', 'Medium', 'High', 'Medium']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Week Number', 'Session Number', 'Category', 'Business Impact', 'Recommendation', 'Resource Type'])
        
        for i, (rec, resource, impact) in enumerate(zip(cost_recommendations, resource_types, business_impacts), 1):
            writer.writerow([i, 1, random.randint(1, 10), 'Cost', impact, rec, resource])
    
    print(f"  ✅ Generado: {filename}")

def generate_comprehensive_csv(output_dir):
    """Generar CSV completo con todas las categorías"""
    filename = os.path.join(output_dir, 'sample_comprehensive_recommendations.csv')
    
    # Combinar recomendaciones de todas las categorías
    all_recommendations = [
        # Security
        ('Security', 'High', 'Virtual machines should have encryption at host enabled', 'Virtual machine'),
        ('Security', 'Medium', 'TLS should be updated to the latest version for web apps', 'App service'),
        ('Security', 'High', 'Machines should be configured to periodically check for missing system updates', 'Virtual machine'),
        ('Security', 'Medium', 'Diagnostic logs in App Service should be enabled', 'App service'),
        ('Security', 'Medium', 'Managed identity should be used in web apps', 'App service'),
        ('Security', 'High', 'Storage account public access should be disallowed', 'Storage Account'),
        
        # Performance
        ('Performance', 'High', 'Right-size or shutdown underutilized virtual machines', 'Virtual machine'),
        ('Performance', 'Medium', 'Enable autoscale to ensure optimal performance', 'App service'),
        ('Performance', 'High', 'Use SSD disks for better IOPS performance', 'Virtual machine'),
        ('Performance', 'Medium', 'Consider using Azure CDN for global content delivery', 'Storage Account'),
        ('Performance', 'High', 'Optimize database query performance', 'Azure SQL Database'),
        
        # Cost
        ('Cost', 'High', 'Consider virtual machine reserved instance to save over your on-demand costs', 'Subscription'),
        ('Cost', 'Medium', 'Consider App Service reserved instance to save over your pay-as-you-go costs', 'Subscription'),
        ('Cost', 'High', 'Consider Database for PostgreSQL reserved instance to save over your pay-as-you-go costs', 'Subscription'),
        ('Cost', 'High', 'Right-size or shutdown underutilized virtual machines', 'Virtual machine'),
        ('Cost', 'Medium', 'Delete unattached disks to save on storage costs', 'Storage Account'),
        
        # Reliability
        ('Reliability', 'High', 'Enable geo-redundant backup for critical databases', 'Azure SQL Database'),
        ('Reliability', 'Medium', 'Implement Azure Site Recovery for disaster recovery', 'Virtual machine'),
        ('Reliability', 'High', 'Configure availability zones for high availability', 'Virtual machine'),
        
        # Operational Excellence
        ('Operational excellence', 'Medium', 'Enable Azure Monitor for better observability', 'Virtual machine'),
        ('Operational excellence', 'Medium', 'Implement Infrastructure as Code with ARM templates', 'Subscription'),
        ('Operational excellence', 'Low', 'Set up automated backup schedules', 'Storage Account')
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Week Number', 'Session Number', 'Category', 'Business Impact', 'Recommendation', 'Resource Type'])
        
        for i, (category, impact, recommendation, resource_type) in enumerate(all_recommendations, 1):
            week = random.randint(1, 4)
            session = random.randint(1, 12)
            writer.writerow([i, week, session, category, impact, recommendation, resource_type])
    
    print(f"  ✅ Generado: {filename}")

def generate_readme():
    """Generar archivo README para los datos de ejemplo"""
    readme_content = """# Datos de Ejemplo - Reportes Especializados Azure

Este directorio contiene archivos CSV de ejemplo para probar la funcionalidad de reportes especializados.

## Archivos Disponibles

### 1. sample_security_recommendations.csv
- **Propósito**: Probar análisis de seguridad especializado
- **Contenido**: 10 recomendaciones de seguridad típicas de Azure Advisor
- **Categorías**: Solo Security
- **Uso**: Ideal para probar SecurityAnalyzer y SecurityHTMLGenerator

### 2. sample_performance_recommendations.csv
- **Propósito**: Probar análisis de rendimiento especializado
- **Contenido**: 8 recomendaciones de performance
- **Categorías**: Solo Performance
- **Uso**: Ideal para probar PerformanceAnalyzer y PerformanceHTMLGenerator

### 3. sample_cost_recommendations.csv
- **Propósito**: Probar análisis de costos especializado
- **Contenido**: 10 recomendaciones de optimización de costos
- **Categorías**: Solo Cost
- **Uso**: Ideal para probar CostAnalyzer y CostHTMLGenerator

### 4. sample_comprehensive_recommendations.csv
- **Propósito**: Probar análisis completo con múltiples categorías
- **Contenido**: 21 recomendaciones mixtas
- **Categorías**: Security, Performance, Cost, Reliability, Operational Excellence
- **Uso**: Ideal para probar análisis completo y comparar con especializados

## Cómo Usar

1. **Subir archivo via interfaz web**:
   - Ve a la página de reportes
   - Sube uno de estos archivos CSV
   - Selecciona el tipo de reporte apropiado
   - Genera el reporte

2. **Usar en tests**:
   ```python
   import pandas as pd
   
   # Cargar datos de prueba
   df = pd.read_csv('backend/sample_data/sample_security_recommendations.csv')
   
   # Usar con analizador
   from apps.reports.utils.specialized_analyzers import SecurityAnalyzer
   analyzer = SecurityAnalyzer(df)
   results = analyzer.analyze()
   ```

3. **Validar funcionalidad**:
   - Los archivos están diseñados para producir resultados realistas
   - Cada tipo debería generar métricas apropiadas
   - Los HTMLs generados deberían mostrar visualizaciones coherentes

## Estructura de Datos

Todos los archivos siguen la estructura estándar de Azure Advisor:

- **Index**: Número secuencial
- **Week Number**: Semana de la recomendación (1-4)
- **Session Number**: Sesión dentro de la semana (1-12)
- **Category**: Categoría de Azure Advisor
- **Business Impact**: Impacto de negocio (High, Medium, Low)
- **Recommendation**: Descripción de la recomendación
- **Resource Type**: Tipo de recurso de Azure afectado

## Resultados Esperados

### Análisis de Seguridad
- **Security Score**: ~60-80 (varía según algoritmo)
- **Critical Issues**: 3-5 issues de alto impacto
- **Compliance Gaps**: Identificación de gaps de encriptación, actualizaciones, etc.

### Análisis de Rendimiento
- **Performance Score**: ~75-90
- **Optimization Potential**: 15-25% de mejora estimada
- **Bottlenecks**: 2-3 cuellos de botella principales

### Análisis de Costos
- **Monthly Savings**: $8,000-15,000 estimado
- **ROI**: 150-300% según implementación
- **Payback Period**: 1-3 meses

¡Usa estos archivos para validar que tu implementación funciona correctamente!
"""
    
    readme_path = 'backend/sample_data/README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  ✅ Generado: {readme_path}")

if __name__ == '__main__':
    generate_sample_csv_data()
    generate_readme()
    
    print("\n🎉 Datos de ejemplo listos para usar!")
    print("\nPróximos pasos:")
    print("1. Sube uno de los archivos CSV generados via interfaz web")
    print("2. Selecciona el tipo de reporte apropiado")
    print("3. Genera el reporte y verifica los resultados")
    print("4. Compara resultados entre tipos especializados y completo")