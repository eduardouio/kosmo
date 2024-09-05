
# Django App

Este proyecto es una aplicación web construida con Django, diseñada para manejar disponibilidad de exportaciones

## Requisitos

Antes de comenzar, asegúrate de tener instalados los siguientes requisitos:

- Python 3.8+
- Django 3.x/4.x (según la versión que estés utilizando)
- pip (gestor de paquetes de Python)
- (Opcional) Virtualenv o venv para crear un entorno virtual

-- delete db.sqlite3
-- find . -path "/migrations/.py" -not -name "init.py" -delete

./manage.py makemigrations accounting accounts companies crm inventary invoices warenhouses

./manage.py migrate

./manage.py sowseed