import json
import random
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel, License
from partners.models import Partner, Contact, Bank, DAE
from products.models import Product, StockDay, StockDetail, BoxItems
from trade.models import (
    Order, OrderItems, Invoice, InvoiceItems, Payment
)


class Command(BaseCommand):
    help = 'This command creates a list of users'

    def handle(self, *args, **options):
        faker = Faker()
        print('creamos el superuser')
        self.createSuperUser()
        print('creamos las licencias')
        self.create_licences()
        print('creamos los clientes')
        self.load_customers()
        print('creamos los proveedores')
        self.load_suppliers()
        print('creamos los contactos')
        self.load_contacts(faker)
        print('creamos los bancos')
        self.load_banks(faker)
        print('creamos los daes')
        self.load_daes(faker)
        print('creamos los productos')
        self.load_products()
        print('creamos los stock_day')
        self.load_stock_day(faker)
        print('creamos los stock_detail')
        self.load_stocks_items()
        print('creamos las ordenes de compra')
        self.load_customer_orders()
        print('creamos las ordenes de compra')
        self.load_purcharse_order()
        print('creamos las facturas de compra')
        self.generarte_purchases_invoices(faker)
        print('Generando facturas de venta')
        self.generate_sales_invoices(faker)
        print('Generando pagos')
        self.generate_payments(faker)

    def createSuperUser(self):
        user = CustomUserModel.get('eduardouio7@gmail.com')
        if user:
            print('Ya existe el usuario')
            return True
        user = CustomUserModel(
            email='eduardouio7@gmail.com',
            is_staff=True,
            is_superuser=True
        )
        user.set_password('seguro')
        user.save()

    def create_licences(self):
        if License.objects.all().count() > 0:
            print('Ya existen licencias')
            return True

        user = CustomUserModel.get('eduardouio7@gmail.com')
        if not user:
            raise Exception('No existe el usuario')

        date_now = datetime.now()

        License.objects.create(
            license_key=secrets.token_urlsafe(50),
            activated_on=date_now,
            expires_on=date_now.replace(year=date_now.year + 1),
            is_active=True,
            url_server='https://dev-7.com/licenses/',
            user=user,
        )

    def load_customers(self):
        if Partner.get_customers().count() > 0:
            print('Ya existen clientes')
            return True

        with open('common/data/customers.json', 'r') as file:
            file_content = json.load(file)

        for customer in file_content:
            print('Creando {} ...'.format(customer['name']))
            Partner.objects.create(
                **customer
            )

    def load_suppliers(self):
        if Partner.get_suppliers().count() > 0:
            print('Ya existen proveedores')
            return True
        user = CustomUserModel.get('eduardouio7@gmail.com')
        if not user:
            raise Exception('No existe el usuario')

        with open('common/data/suppliers.json', 'r') as file:
            file_content = json.load(file)

        for supplier in file_content:
            print('Creando {} ...'.format(supplier['name']))
            Partner.objects.create(
                **supplier
            )

    def load_contacts(self, faker):
        if Contact.objects.all().count() > 0:
            print('Ya existen contactos')
            return True

        partners = Partner.objects.all()

        for partner in partners:
            for _ in range(random.randint(1, 4)):
                print('Creando contacto para {} ...'.format(partner.name))
                Contact.objects.create(
                    partner=partner,
                    name=faker.name(),
                    position=[
                        'Logistica',
                        'Financiero',
                        'Comercial',
                        'Otro'
                    ][random.randint(0, 3)],
                    phone=faker.phone_number(),
                    email=faker.email(),
                    is_principal=faker.boolean()
                )

    def load_banks(self, faker):
        if Bank.objects.all().count() > 0:
            print('Ya existen bancos')
            return True

        banks = ['Banco Internacional', 'Banco Pichincha', 'Banco del Austro',
                 'Banco de Guayaquil', 'Banco de Loja'
                 ]

        partners = Partner.objects.all()

        for partner in partners:
            for _ in range(random.randint(1, 3)):
                print('Creando banco para {} ...'.format(partner.name))
                Bank.objects.create(
                    partner=partner,
                    bank_name=banks[random.randint(0, 4)],
                    owner=faker.name(),
                    id_owner=faker.ssn(),
                    account_number=faker.iban(),
                    national_bank=faker.boolean()
                )

    def load_daes(self, faker):
        if DAE.objects.all().count() > 0:
            print('Ya existen daes')
            return True
        suppliers = Partner.get_suppliers()
        date_now = datetime.now()
        for supplier in suppliers:
            dae = '055-2024-80-0{}'.format(faker.random_int(13, 1327)*15231)
            print('Creando DAE para {} -> {} ...'.format(supplier.name, dae))
            DAE.objects.create(
                partner=supplier,
                dae=dae,
                date_begin=date_now,
                date_end=date_now.replace(month=date_now.month + 1)
            )

    def load_products(self):
        if Product.objects.all().count() > 0:
            print('Ya existen productos')
            return True
        with open('common/data/products.json', 'r') as file:
            file_content = json.load(file)

        for product in file_content:
            print('Creando {} ...'.format(product['name']))
            Product.objects.create(
                **product
            )

    def load_stock_day(self, faker):
        if StockDay.objects.all().count() > 0:
            print('Ya existen stock_day')
            return True
        for i in range(1, 10):
            print('Creando stock_day {}'.format(i))
            StockDay.objects.create(
                date=faker.date_this_year()
            )

    def load_stocks_items(self):
        if StockDetail.objects.count() > 0:
            print('Ya existen stock_detail')
            return True
        partners = Partner.get_suppliers()
        products = Product.objects.all()
        stock_days = StockDay.objects.all()
        colors_available = [
            "WHITE", "LAVENDER", "YELLOW", "YELLOW & ORANGE", "ORANGE", "PINK",
            "HOT PINK", "LIGHT PINK", "PEACHY PINK", "RED", "PEACH & APRICOT",
            "STAND COLOR", "LILAC", "PEACH APRICOT", "LIGHT BROWN"
        ]
        qty_stems = {
            'HB': [25, 30, 35, 40, 45],
            'QB': [50, 60, 70],
        }
        cost_references = {
            '40': [0.40, 0.41, 0.43, 0.45, 0.47, 0.49],
            '50': [0.50, 0.51, 0.53, 0.55, 0.57, 0.59],
            '60': [0.60, 0.61, 0.63, 0.65, 0.67, 0.69],
            '70': [0.70, 0.71, 0.73, 0.75, 0.77, 0.79],
            '80': [0.70, 0.71, 0.73, 0.75, 0.77, 0.79],
            '90': [0.70, 0.71, 0.73, 0.75, 0.77, 0.79],
        }
        for stock_day in stock_days:
            print('Creando stock_detail para {}'.format(stock_day.date))
            for partner in partners:
                for i in range(0, random.randint(50, 123)):
                    box_model = random.choice(['HB', 'QB', 'QB', 'QB', 'HB'])
                    qty_stem = random.choice(qty_stems[box_model])
                    product = products[random.randint(0, products.count() - 1)]
                    length = random.choice([40, 50, 60, 70, 80, 90])

                    stock_detail = StockDetail.objects.create(
                        stock_day=stock_day,
                        partner=partner,
                        box_model=box_model,
                        tot_stem_flower=qty_stem,
                        stem_cost_price=random.choice(
                            cost_references[str(length)])
                    )

                    BoxItems.objects.create(
                        stock_detail=stock_detail,
                        product=product,
                        length=length,
                        qty_stem_flower=qty_stem
                    )

    def load_customer_orders(self):
        if Order.objects.filter(type_document="ORD_VENTA").count() > 0:
            print('Ya existen ordenes de venta')
            return True

        stock_days = StockDay.objects.all()

        for order in range(1, random.randint(10, 35)):
            print('Creando orden de compra {}'.format(order))
            customers = Partner.get_customers()
            order_sale = Order.objects.create(
                date=datetime.now(),
                partner=customers[random.randint(0, customers.count() - 1)],
                type_document='ORD_VENTA',
                status='PENDIENTE',
            )

            print('Creando detalles de orden de venta')
            for i in range(1, random.randint(1, 6)):
                stock_day = stock_days[random.randint(
                    0, stock_days.count() - 1)
                ]
                stock_day_detail = StockDetail.objects.filter(
                    stock_day=stock_day
                )

                line_stock = stock_day_detail[random.randint(
                    0, stock_day_detail.count() - 1)]

                line_price = (
                    line_stock.stem_cost_price
                    * line_stock.tot_stem_flower
                    * Decimal(1.06)
                )

                OrderItems.objects.create(
                    order=order_sale,
                    stock_detail=line_stock,
                    line_price=line_price,
                    qty_stem_flower=line_stock.tot_stem_flower
                )

    def load_purcharse_order(self):
        if Order.objects.filter(type_document="ORD_COMPRA").count() > 0:
            print('Ya existen ordenes de compra')
            return True

        order_sales = Order.objects.filter(type_document="ORD_VENTA")

        for order in order_sales:
            suppliers = OrderItems.get_suppliers_by_order(order)
            for supplier in suppliers:
                order_purchase = Order.objects.create(
                    date=datetime.now(),
                    partner=supplier,
                    type_document='ORD_COMPRA',
                    parent_order=order,
                    status='PENDIENTE',
                )

                order_items = OrderItems.get_supplier_items_by_order(
                    supplier, order
                )

                for item in order_items:
                    OrderItems.objects.create(
                        order=order_purchase,
                        stock_detail=item.stock_detail,
                        line_price=item.line_price,
                        qty_stem_flower=item.qty_stem_flower,
                    )

    def generarte_purchases_invoices(self, faker):
        if Invoice.objects.filter(type_document="FAC_COMPRA").count() > 0:
            print('Ya existen facturas de compra')
            return True

        purchase_orders = Order.objects.filter(type_document="ORD_COMPRA")

        for order in purchase_orders:
            date = faker.date_this_year()
            due_date = date + timedelta(days=90)
            invoice = Invoice.objects.create(
                order=order,
                partner=order.partner,
                num_invoice=Invoice.get_next_invoice_number(),
                type_document='FAC_COMPRA',
                type_invoice='NA',
                date=date,
                due_date=due_date,
                status='PENDIENTE'
            )

            order_items = OrderItems.objects.filter(order=order)
            for item in order_items:
                InvoiceItems.objects.create(
                    invoice=invoice,
                    order_item=item,
                    qty_stem_flower=item.qty_stem_flower,
                    line_price=item.line_price,
                    line_discount=0,
                )

    def generate_sales_invoices(self, faker):
        # se genera a partir de la orden de compra
        if Invoice.objects.filter(type_document="FAC_VENTA").count() > 0:
            print('Ya existen facturas de venta')
            return True

        purchase_orders = Order.objects.filter(type_document="ORD_COMPRA")

        for order in purchase_orders:
            print('Generando Factura de venta de order ' + str(order.id))
            date = faker.date_this_year()
            due_date = date + timedelta(days=90)
            invoice = Invoice.objects.create(
                order=order,
                partner=order.parent_order.partner,
                num_invoice=Invoice.get_next_invoice_number(),
                type_document='FAC_VENTA',
                type_invoice='EXPORT',
                date=date,
                due_date=due_date,
                status='PENDIENTE'
            )

            order_items = OrderItems.objects.filter(order=order)
            for item in order_items:
                InvoiceItems.objects.create(
                    invoice=invoice,
                    order_item=item,
                    qty_stem_flower=item.qty_stem_flower,
                    line_price=item.line_price,
                    line_discount=0,
                )

    def generate_payments(self, faker):
        if Payment.objects.all().count() > 0:
            print('Ya existen pagos')
            return True

        sales_invoices = Invoice.get_by_type('FAC_VENTA')
        purchase_invoices = Invoice.get_by_type('FAC_COMPRA')

        # cobros en ventas
        for i in range(random.randint(10, 25)):
            invoices = [
                sales_invoices[random.randint(0, sales_invoices.count() - 1)],
                sales_invoices[random.randint(0, sales_invoices.count() - 1)],
            ]
            payment = Payment.objects.create(
                date=faker.date_this_year(),
                amount=random.randint(10, 50),
                method='EFECTIVO',
            )

            for i in invoices:
                payment.invoices.add(i)
                payment.save()

        # pagos en compras
        for i in range(random.randint(10, 25)):
            invoices = [
                purchase_invoices[random.randint(
                    0, purchase_invoices.count() - 1)
                ],
                purchase_invoices[random.randint(
                    0, purchase_invoices.count() - 1)
                ],
            ]
            payment = Payment.objects.create(
                date=faker.date_this_year(),
                amount=random.randint(10, 50),
                method='EFECTIVO',
            )

            for i in invoices:
                payment.invoices.add(i)
                payment.save()
