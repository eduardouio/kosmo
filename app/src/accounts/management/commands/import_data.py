import json
import os
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Importa datos desde archivos JSON a sus respectivos modelos en la base de datos'

    def handle(self, *args, **kwargs):
        data_folder = 'tests/testdata/'
        
        if not os.path.exists(data_folder):
            self.stdout.write(self.style.ERROR(f'El directorio {data_folder} no existe.'))
            return

        for filename in os.listdir(data_folder):
            if filename.endswith('_exportados.json'):
                app_label, model_name = filename.replace('_exportados.json', '').split('_', 1)
                
                try:
                    model = apps.get_model(app_label, model_name.capitalize())
                except LookupError:
                    self.stdout.write(self.style.ERROR(f'No se encontró el modelo {model_name} en la aplicación {app_label}.'))
                    continue
                
                file_path = os.path.join(data_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    records = json.load(file)
                
                for record in records:
                    record_id = record.pop('id', None)  # Eliminar ID para evitar conflictos
                    obj, created = model.objects.update_or_create(defaults=record, id=record_id)
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Registro creado en {model_name}: {obj}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Registro actualizado en {model_name}: {obj}'))

        self.stdout.write(self.style.SUCCESS('Importación completada exitosamente.'))
