from django.core.management.base import BaseCommand
from trade.models import Invoice


class Command(BaseCommand):
    help = (
        'Actualiza el estado de pago de todas las facturas '
        'basado en los pagos confirmados'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra los cambios sin aplicarlos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                'Modo dry-run: Solo mostrando cambios sin aplicar'
            )
        
        updated_count = 0
        total_count = 0
        
        for invoice in Invoice.objects.filter(is_active=True):
            total_count += 1
            old_status = invoice.status
            
            # Calcular si debería estar pagada
            if invoice.is_fully_paid:
                new_status = 'PAGADO'
            else:
                new_status = 'PENDIENTE'
            
            if old_status != new_status and old_status != 'ANULADO':
                updated_count += 1
                self.stdout.write(
                    f'Factura {invoice.id}: {old_status} -> {new_status} '
                    f'(Pagado: ${invoice.total_paid} / '
                    f'Total: ${invoice.total_invoice})'
                )
                
                if not dry_run:
                    invoice.status = new_status
                    invoice.save()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Se actualizarían {updated_count} de '
                    f'{total_count} facturas'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Actualizadas {updated_count} de {total_count} facturas'
                )
            )
