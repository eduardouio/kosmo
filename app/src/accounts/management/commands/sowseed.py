import json
import random
import secrets
from datetime import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel, License
from partners.models import Partner, Contact, Bank, DAE


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
            dae = '055-2024-80-0{}'.format(faker.random_int(123, 1232)*1523)
            print('Creando DAE para {} -> {} ...'.format(supplier.name, dae))
            DAE.objects.create(
                partner=supplier,
                dae=dae,
                date_begin=date_now,
                date_end=date_now.replace(month=date_now.month + 1)
            )
