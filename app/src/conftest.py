import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase
from django.test.utils import teardown_test_environment, setup_test_environment


@pytest.fixture(scope='session')
def django_db_setup():
    db_path = settings.DATABASES['default']['NAME']
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_path,
        'ATOMIC_REQUESTS': True,
    }

    # call_command('loaddata', 'initial_data.json', verbosity=0)

    def django_db_keep_data(request, django_db_setup, django_db_blocker):
        """Keep data in database after tests."""
        with django_db_blocker.unblock():
            yield

        TransactionTestCase.reset_sequences(None)
        call_command('flush', verbosity=0, interactive=False)
