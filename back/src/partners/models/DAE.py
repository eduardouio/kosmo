from django.db import models
from .Partner import Partner


class DAE(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE
    )
    dae = models.CharField(
        'DAE',
        max_length=50,
        unique=True
    )
    date_begin = models.DateField(
        'Fecha de Inicio',
    )
    date_end = models.DateField(
        'Fecha de Fin',
    )

    def __str__(self):
        return '{} {}'.format(self.dae, self.partner)

    class Meta:
        verbose_name = 'DAE'
        verbose_name_plural = 'DAEs'
        db_table = 'dae'
        unique_together = ('dae', 'partner')
