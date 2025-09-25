# apps/reports/migrations/0002_fix_csv_file_constraint.py
# Ejecutar: python manage.py makemigrations reports --name fix_csv_file_constraint
# Luego: python manage.py migrate

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        # OPCIÓN 1: Hacer csv_file opcional (recomendado para flexibilidad)
        migrations.AlterField(
            model_name='report',
            name='csv_file',
            field=models.ForeignKey(
                blank=True,
                null=True,  # ← Permitir null
                on_delete=django.db.models.deletion.SET_NULL,  # ← No CASCADE
                related_name='reports',
                to='reports.csvfile'
            ),
        ),
        
        # OPCIÓN 2: Agregar índice para mejorar rendimiento
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['csv_file'], name='reports_rep_csv_fil_idx'),
        ),
    ]