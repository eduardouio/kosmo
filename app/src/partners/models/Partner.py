from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from common import BaseModel

PARTNER_TYPE_CHOICES = [
    ('CLIENTE', 'CLIENTE'),
    ('PROVEEDOR', 'PROVEEDOR'),
]

STATUS = (
    ('APROBADO', 'APROBADO'),
    ('RECHAZADO', 'RECHAZADO'),
    ('PENDIENTE', 'PENDIENTE'),
)


# el cliente solo recibe las disponibilidades de los productos de ciertas
# fincas o proveedor de kosmo
class Partner(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    business_tax_id = models.CharField(
        'RUC',
        max_length=15,
    )
    partner = models.ManyToManyField(
        "self",
        blank=True,
        help_text="proveedores a los que los clientes pueden comprar",
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS,
        default='APROBADO',
    )
    date_aproved = models.DateField(
        'Fecha de Aprobación',
        blank=True,
        null=True,
        help_text="Fecha en que el socio fue aprobado para operar"
    )
    short_name = models.CharField(
        'Nombre Corto',
        max_length=50,
        blank=True,
        null=True,
        default=None
    )
    address = models.CharField(
        'Dirección',
        max_length=255
    )
    country = models.CharField(
        'País',
        max_length=50
    )
    area_code = models.CharField(
        'Código de Área',
        max_length=10,
        blank=True,
        null=True
    )
    city = models.CharField(
        'Ciudad',
        max_length=50
    )
    zip_code = models.CharField(
        'Código Postal',
        max_length=10,
        blank=True,
        null=True
    )
    website = models.CharField(
        'Sitio Web',
        max_length=255,
        blank=True,
        null=True
    )
    is_profit_margin_included = models.BooleanField(
        'Margen Incluido',
        default=False
    )
    default_profit_margin = models.DecimalField(
        'Rendimiento por defecto',
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    credit_term = models.IntegerField(
        'Plazo de crédito',
        help_text="Tiempo de crédito en días, cero para prepago",
        default=0
    )
    phone = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True,
        null=True
    )
    skype = models.CharField(
        'Teams',
        max_length=50,
        blank=True,
        null=True
    )
    dispatch_address = models.CharField(
        'Dirección de Envío',
        max_length=255,
        blank=True,
        null=True
    )
    email = models.EmailField(
        'Correo Electrónico',
        max_length=255,
        blank=True,
        null=True
    )
    email_payment = models.EmailField(
        'Correo Electrónico de Pago',
        max_length=255,
        blank=True,
        null=True
    )
    dispatch_days = models.PositiveIntegerField(
        'Días de Envío',
        blank=True,
        null=True
    )
    cargo_reference = models.CharField(
        'Referencia de Carga',
        max_length=255,
        blank=True,
        null=True,
        help_text="Es el transportista que se usa para enviar la carga"
    )
    type_partner = models.CharField(
        'Tipo de Socio',
        max_length=50,
        choices=PARTNER_TYPE_CHOICES,
    )
    businnes_start = models.DateField(
        'Años en el mercado',
        blank=True,
        null=True
    )
    consolidate = models.BooleanField(
        'Consolidado',
        default=False
    )
    reference_1 = models.CharField(
        'Referencia 1',
        max_length=255,
        blank=True,
        null=True
    )
    contact_reference_1 = models.CharField(
        'Contacto Referencia 1',
        max_length=255,
        blank=True,
        null=True
    )
    phone_reference_1 = models.CharField(
        'Teléfono Referencia 1',
        max_length=20,
        blank=True,
        null=True
    )
    reference_2 = models.CharField(
        'Referencia 2',
        max_length=255,
        blank=True,
        null=True
    )
    contact_reference_2 = models.CharField(
        'Contacto Referencia 2',
        max_length=255,
        blank=True,
        null=True
    )
    phone_reference_2 = models.CharField(
        'Teléfono Referencia 2',
        max_length=20,
        blank=True,
        null=True
    )
    is_verified = models.BooleanField(
        'Verificado',
        default=False
    )
    seller = models.CharField(
        'Vendedor',
        max_length=100,
        blank=True,
        null=True,
        help_text="Vendedor asignado al cliente"
    )
    id_seller = models.PositiveSmallIntegerField(
        "Usuario Asociado",
        default=0,
        blank=True,
        null=True,
    )
    years_in_market = models.PositiveIntegerField(
        'Años en el mercado',
        blank=True,
        null=True,
        default=0,
        help_text="Años que el socio ha estado en el mercado"
    )

    @classmethod
    def get_customers(cls):
        return cls.objects.filter(
            type_partner='CLIENTE',
            is_active=True
        )

    @classmethod
    def get_suppliers(cls):
        return cls.objects.filter(
            type_partner='PROVEEDOR',
            is_active=True
        )

    @classmethod
    def get_parent_suppliers(cls, partner):
        all_partners_for_parent = []
        list_suppliers = []
        if partner.type_partner == 'CLIENTE':
            all_partners_for_parent = cls.get_suppliers()
        else:
            all_partners_for_parent = cls.get_customers()

        for itm in all_partners_for_parent:
            parent_partner = {
                'suplier': itm,
                'selected': False
            }

            if itm in partner.partner.all():
                parent_partner['selected'] = True

            list_suppliers.append(parent_partner)

        order_list = [
            x for x in list_suppliers if x['selected']
        ] + [
            x for x in list_suppliers if not x['selected']
        ]

        return order_list

    @classmethod
    def get_partner_by_taxi_id(cls, business_tax_id):
        try:
            return cls.objects.get(
                business_tax_id=business_tax_id
            )
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_by_parcial_name(cls, name):
        partners = cls.objects.filter(
            name__icontains=name
        )
        return partners[0] if partners else None

    def __str__(self):
        return self.name
