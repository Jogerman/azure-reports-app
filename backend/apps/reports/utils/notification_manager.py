# backend/apps/reports/utils/notification_manager.py
"""
Sistema de notificaciones para reportes completados
"""

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import Dict, Any, List
import requests

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gestor de notificaciones para reportes"""
    
    @staticmethod
    def notify_report_completed(report, user_email: str = None) -> bool:
        """Notificar cuando un reporte esté completado"""
        try:
            email_sent = NotificationManager._send_email_notification(report, user_email)
            
            # Intentar notificación por Slack si está configurado
            slack_sent = NotificationManager._send_slack_notification(report)
            
            # Intentar notificación por Teams si está configurado  
            teams_sent = NotificationManager._send_teams_notification(report)
            
            return email_sent or slack_sent or teams_sent
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones para reporte {report.id}: {e}")
            return False
    
    @staticmethod
    def _send_email_notification(report, user_email: str = None) -> bool:
        """Enviar notificación por email"""
        try:
            if not user_email:
                user_email = report.user.email
            
            if not user_email:
                logger.warning(f"No hay email para usuario {report.user.username}")
                return False
            
            # Renderizar template de email
            context = {
                'report': report,
                'report_type_display': report.get_report_type_display(),
                'completion_date': report.completed_at,
                'pdf_url': report.pdf_url,
                'html_url': f"{settings.FRONTEND_URL}/reports/{report.id}/view" if hasattr(settings, 'FRONTEND_URL') else None
            }
            
            html_message = render_to_string('emails/report_completed.html', context)
            plain_message = render_to_string('emails/report_completed.txt', context)
            
            send_mail(
                subject=f'✅ Reporte Azure Completado: {report.title}',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"📧 Email enviado a {user_email} para reporte {report.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    @staticmethod
    def _send_slack_notification(report) -> bool:
        """Enviar notificación a Slack"""
        try:
            slack_webhook = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            if not slack_webhook:
                return False
            
            # Obtener métricas del reporte para mostrar en Slack
            analysis_summary = ""
            if report.analysis_results:
                if report.report_type == 'security':
                    security_data = report.analysis_results.get('security_analysis', {})
                    dashboard_metrics = security_data.get('dashboard_metrics', {})
                    analysis_summary = f"""
🔐 *Security Score*: {dashboard_metrics.get('security_score', 0)}/100
🚨 *Critical Issues*: {dashboard_metrics.get('critical_issues', 0)}
⏰ *Working Hours*: {dashboard_metrics.get('working_hours', 0)}h
                    """.strip()
                elif report.report_type == 'cost':
                    cost_data = report.analysis_results.get('cost_analysis', {})
                    dashboard_metrics = cost_data.get('dashboard_metrics', {})
                    analysis_summary = f"""
💰 *Monthly Savings*: ${dashboard_metrics.get('monthly_savings', 0):,.0f}
📊 *ROI*: {dashboard_metrics.get('roi_percentage', 0):.1f}%
⏱️ *Payback*: {dashboard_metrics.get('payback_months', 0)} months
                    """.strip()
            
            # Crear payload para Slack
            payload = {
                "text": f"🎉 Reporte Azure Completado",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {
                                "title": "Título del Reporte",
                                "value": report.title,
                                "short": False
                            },
                            {
                                "title": "Tipo",
                                "value": report.get_report_type_display(),
                                "short": True
                            },
                            {
                                "title": "Usuario",
                                "value": report.user.get_full_name() or report.user.username,
                                "short": True
                            }
                        ],
                        "actions": [
                            {
                                "type": "button",
                                "text": "Ver Reporte 📊",
                                "url": f"{settings.FRONTEND_URL}/reports/{report.id}/view" if hasattr(settings, 'FRONTEND_URL') else "#"
                            },
                            {
                                "type": "button", 
                                "text": "Descargar PDF 📄",
                                "url": report.pdf_url or "#"
                            }
                        ]
                    }
                ]
            }
            
            # Agregar métricas si están disponibles
            if analysis_summary:
                payload["attachments"][0]["fields"].append({
                    "title": "Métricas Principales",
                    "value": analysis_summary,
                    "short": False
                })
            
            response = requests.post(slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"📢 Notificación Slack enviada para reporte {report.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación Slack: {e}")
            return False
    
    @staticmethod
    def _send_teams_notification(report) -> bool:
        """Enviar notificación a Microsoft Teams"""
        try:
            teams_webhook = getattr(settings, 'TEAMS_WEBHOOK_URL', None)
            if not teams_webhook:
                return False
            
            # Crear adaptive card para Teams
            card_payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": f"Reporte Azure Completado: {report.title}",
                "sections": [
                    {
                        "activityTitle": "🎉 Reporte Azure Completado",
                        "activitySubtitle": f"**{report.title}**",
                        "activityImage": "https://docs.microsoft.com/en-us/azure/media/index/azure-germany.svg",
                        "facts": [
                            {
                                "name": "Tipo de Reporte:",
                                "value": report.get_report_type_display()
                            },
                            {
                                "name": "Usuario:",
                                "value": report.user.get_full_name() or report.user.username
                            },
                            {
                                "name": "Completado:",
                                "value": report.completed_at.strftime("%Y-%m-%d %H:%M")
                            }
                        ],
                        "markdown": True
                    }
                ],
                "potentialAction": [
                    {
                        "@type": "OpenUri",
                        "name": "Ver Reporte",
                        "targets": [
                            {
                                "os": "default",
                                "uri": f"{settings.FRONTEND_URL}/reports/{report.id}/view" if hasattr(settings, 'FRONTEND_URL') else "#"
                            }
                        ]
                    }
                ]
            }
            
            if report.pdf_url:
                card_payload["potentialAction"].append({
                    "@type": "OpenUri", 
                    "name": "Descargar PDF",
                    "targets": [
                        {
                            "os": "default",
                            "uri": report.pdf_url
                        }
                    ]
                })
            
            response = requests.post(teams_webhook, json=card_payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"📢 Notificación Teams enviada para reporte {report.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación Teams: {e}")
            return False
