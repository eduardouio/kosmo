from common import BaseModel
from django.db import models
from django.core.exceptions import ValidationError
from trade.models import Invoice


METHOD_CHOICES = (
    ('TRANSF', 'TRANSFERENCIA'),
    ('CHEQUE', 'CHEQUE'),
    ('EFECTIVO', 'EFECTIVO'),
    ('OTRO', 'OTRO'),
    ('TC', 'TARJETA DE CRÉDITO'),
    ('TD', 'TARJETA DE DÉBITO'),
    ('NC', 'NOTA DE CRÉDITO')
)

TYPE = (
    ('INGRESO', 'INGRESO'),
    ('EGRESO', 'EGRESO')
)

STATUS_CHOICES = (
    ('PENDIENTE', 'PENDIENTE'),
    ('CONFIRMADO', 'CONFIRMADO'),
    ('RECHAZADO', 'RECHAZADO'),
    ('ANULADO', 'ANULADO')
)


class Payment(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    invoices = models.ManyToManyField(
        'trade.Invoice'
    )
    payment_number = models.CharField(
        'Número de Pago',
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )
    date = models.DateField(
        'Fecha de pago'
    )
    due_date = models.DateField(
        'Fecha de vencimiento',
        blank=True,
        null=True
    )
    type_transaction = models.CharField(
        'Tipo de Transacción',
        max_length=10,
        choices=TYPE,
        default='INGRESO'
    )
    amount = models.DecimalField(
        'Monto',
        max_digits=15,
        decimal_places=2
    )
    method = models.CharField(
        'Método de pago',
        max_length=50,
        choices=METHOD_CHOICES,
        default='OTRO'
    )
    status = models.CharField(
        'Estado',
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDIENTE'
    )
    bank = models.CharField(
        'Banco',
        max_length=100,
        blank=True,
        null=True
    )
    nro_account = models.CharField(
        'Nro de Cuenta',
        max_length=50,
        blank=True,
        null=True
    )
    nro_operation = models.CharField(
        'Nro de Operación',
        max_length=50,
        blank=True,
        null=True
    )
    document = models.ImageField(
        'Documento',
        upload_to='payments/',
        blank=True,
        null=True
    )
    processed_by = models.ForeignKey(
        'accounts.CustomUserModel',
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name='processed_payments',
        help_text='Usuario que procesó el pago'
    )
    approved_by = models.ForeignKey(
        'accounts.CustomUserModel',
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name='approved_payments',
        help_text='Usuario que aprobó el pago'
    )
    approval_date = models.DateTimeField(
        'Fecha de Aprobación',
        blank=True,
        null=True
    )

    @property
    def is_overdue(self):
        """Verifica si el pago está vencido"""
        if self.due_date and self.status == 'PENDIENTE':
            from datetime import date
            return date.today() > self.due_date
        return False

    @property
    def total_invoices_amount(self):
        """Calcula el total de las facturas asociadas"""
        return sum(invoice.total_invoice for invoice in self.invoices.all())

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()

        # Validar que el monto sea positivo
        if self.amount <= 0:
            raise ValidationError('El monto debe ser mayor a cero')

        # Validar campos requeridos según el método de pago
        if self.method in ['TRANSF', 'TC', 'TD']:
            if not self.bank:
                raise ValidationError(
                    'El banco es requerido para este método de pago')
            if not self.nro_operation:
                raise ValidationError(
                    'El número de operación es requerido para este método de pago')

        # Validar que la fecha de vencimiento sea posterior a la fecha de pago
        if self.due_date and self.due_date < self.date:
            raise ValidationError(
                'La fecha de vencimiento no puede ser anterior a la fecha de pago')

    @classmethod
    def get_by_status(cls, status):
        """Obtiene pagos por estado"""
        return cls.objects.filter(status=status, is_active=True)

    @classmethod
    def get_pending_payments(cls):
        """Obtiene pagos pendientes"""
        return cls.get_by_status('PENDIENTE')

    @classmethod
    def get_overdue_payments(cls):
        """Obtiene pagos vencidos"""
        from datetime import date
        return cls.objects.filter(
            status='PENDIENTE',
            due_date__lt=date.today(),
            is_active=True
        )

    @classmethod
    def get_payments_by_invoice(cls, invoice):
        """Obtiene pagos asociados a una factura"""
        return cls.objects.filter(invoices=invoice, is_active=True)

    @classmethod
    def get_payments_by_date_range(cls, start_date, end_date):
        """Obtiene pagos en un rango de fechas"""
        return cls.objects.filter(
            date__range=[start_date, end_date],
            is_active=True
        )

    @classmethod
    def get_next_payment_number(cls):
        """Genera el siguiente número de pago"""
        last_payment = cls.objects.filter(
            payment_number__isnull=False
        ).order_by('-id').first()

        if last_payment and last_payment.payment_number:
            try:
                last_number = int(last_payment.payment_number.split('-')[-1])
                return f"PAY-{last_number + 1:06d}"
            except (ValueError, IndexError):
                pass

        return "PAY-000001"

    @classmethod
    def get_net_collection_number(cls):
        """Genera el siguiente número de recaudación neta"""
        last_collection = cls.objects.filter(
            net_collection_number__isnull=False
        ).order_by('-id').first()

        if last_collection and last_collection.net_collection_number:
            try:
                last_number = int(
                    last_collection.net_collection_number.split('-')[-1])
                return f"COL-{last_number + 1:06d}"
            except (ValueError, IndexError):
                pass

        return "COL-000001"

    def __str__(self):
        return f"Pago {self.payment_number or self.id} - {self.amount}"

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
