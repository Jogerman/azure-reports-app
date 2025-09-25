# apps/reports/management/commands/clear_report_cache.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.reports.utils.cache_manager import ReportCacheManager

class Command(BaseCommand):
    help = 'Limpia el caché de reportes HTML'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report-id',
            type=int,
            help='ID específico del reporte a limpiar',
        )

    def handle(self, *args, **options):
        if options['report_id']:
            from apps.reports.models import Report
            try:
                report = Report.objects.get(id=options['report_id'])
                ReportCacheManager.invalidate_cache(report)
                self.stdout.write(
                    self.style.SUCCESS(f'Caché limpiado para reporte {report.id}')
                )
            except Report.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Reporte {options["report_id"]} no encontrado')
                )
        else:
            # Limpiar todo el caché de reportes
            cache.delete_pattern(f"{ReportCacheManager.CACHE_PREFIX}_*")
            self.stdout.write(
                self.style.SUCCESS('Todo el caché de reportes ha sido limpiado')
            )