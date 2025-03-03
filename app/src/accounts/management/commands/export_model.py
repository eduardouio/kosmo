import json
from django.core.management.base import BaseCommand
from django.apps import apps
from datetime import datetime, date
from decimal import Decimal

class Command(BaseCommand):
    help = 'Exporta los datos de todos los modelos de todas las aplicaciones a archivos JSON'

    def handle(self, *args, **kwargs):
        def custom_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return float(obj)  # También podrías usar str(obj) si prefieres conservar precisión
            raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                model_name = model.__name__
                filename = f'{app_config.label}_{model_name.lower()}_exportados.json'
                
                records = list(model.objects.all().values())
                records_json = json.dumps(records, indent=4, default=custom_serializer)
                
                with open('tests/testdata/' + filename, 'w', encoding='utf-8') as file:
                    file.write(records_json)
                
                self.stdout.write(self.style.SUCCESS(f'Datos exportados exitosamente a {filename}'))
