from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from common import BaseModel

PARTNER_TYPE_CHOICES = [
    ('CLIENTE', 'CLIENTE'),
    ('PROVEEDOR', 'PROVEEDOR'),
]


# el cliente solo recibe las disponibilidades de los productos de ciertas
# fincas o proveedor de kosmo
class Partner(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    business_tax_id = models.CharField(
        'RUC',
        max_length=15,
        unique=True
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
    address = models.CharField(
        'Dirección',
        max_length=255
    )
    country = models.CharField(
        'País',
        max_length=50
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
        'Skype',
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

    @classmethod
    def get_customers(cls):
        return cls.objects.filter(
            type_partner='CLIENTE'
        )

    @classmethod
    def get_suppliers(cls):
        return cls.objects.filter(
            type_partner='PROVEEDOR'
        )

    @classmethod
    def get_registered_suppliers(cls, supplier):
        if supplier.type_partner == 'PROVEEDOR':
            return []

        all_suppliers = cls.get_suppliers()
        supplier_partners = supplier.partner.all()
        list_suppliers = []
        for itm in all_suppliers:
            partner = {
                'suplier': itm,
                'selected': False
            }
            if itm in supplier_partners:
                partner['selected'] = True

            list_suppliers.append(partner)
        return list_suppliers

    @classmethod
    def get_partner_by_taxi_id(cls, business_tax_id):
        try:
            return cls.objects.get(
                business_tax_id=business_tax_id
            )
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_partner_by_id(cls, id):
        try:
            return cls.objects.get(
                id=id
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
        if self.type_partner == 'client':
            return f'C: {self.name}'
        return f'S: {self.name}'
