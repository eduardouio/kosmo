import json
import random
import secrets
from faker import Faker
from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel, License
from partners.models import Partner


class Command(BaseCommand):
    help = 'This command creates a list of users'

    def handle(self, *args, **options):
        faker = Faker()
        print('creamos el superuser')
        self.createSuperUser()
        print('creamos las licencias')
        self.create_licences(faker)
        print('creamos los clientes')
        self.load_customers(faker)

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

    def create_licences(self, faker):
        if license.objects.all().count() > 0:
            print('Ya existen licencias')
            return True

        user = CustomUserModel.get('eduardouio7@gmail.com')
        if not user:
            raise Exception('No existe el usuario')

        License.objects.create(
            license_key=secrets.token_urlsafe(50),
            activated_on=faker.date_time_this_year(),
            expires_on=faker.date_time_next_year(),
            datetime_start=faker.date_time_this_year(),
            datetime_end=faker.date_time_this_year(),
            is_active=True,
            url_server='https://dev-7.com/licenses/',
            user=user,
        )

    def load_customers(self, faker):
        with open('common/data/customers.json', 'r') as file:
            file_content = json.load(file)

        for customer in file_content:
            Partner.objects.create(
                **customer
            )
