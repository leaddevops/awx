# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved.

# Python
import json

# Django
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

# Tower
from awx.main.models.base import CreatedModifiedModel


class TowerSettings(CreatedModifiedModel):

    class Meta:
        app_label = 'main'

    SETTINGS_TYPE_CHOICES = [
        ('string', _("String")),
        ('int', _('Integer')),
        ('float', _('Decimal')),
        ('json', _('JSON')),
        ('bool', _('Boolean')),
        ('password', _('Password')),
        ('list', _('List'))
    ]

    key = models.CharField(
        max_length=255,
        unique=True
    )
    description = models.TextField()
    category = models.CharField(max_length=128)
    value = models.TextField(
        blank=True,
    )
    value_type = models.CharField(
        max_length=12,
        choices=SETTINGS_TYPE_CHOICES
    )
    user = models.ForeignKey(
        'auth.User',
        related_name='settings',
        default=None,
        null=True,
        editable=False,
    )

    @property
    def value_converted(self):
        if self.value_type == 'json':
            converted_type = json.loads(self.value)
        elif self.value_type == 'password':
            converted_type = self.value
        elif self.value_type == 'list':
            if self.value:
                converted_type = [x.strip() for x in self.value.split(',')]
            else:
                converted_type = []
        elif self.value_type == 'bool':
            converted_type = force_text(self.value).lower() in ('true', 'yes', '1')
        elif self.value_type == 'string':
            converted_type = self.value
        else:
            t = __builtins__[self.value_type]
            converted_type = t(self.value)
        return converted_type

    @value_converted.setter
    def value_converted(self, value):
        if self.value_type == 'json':
            self.value = json.dumps(value)
        elif self.value_type == 'list':
            try:
                self.value = ','.join(map(force_text, value))
            except TypeError:
                self.value = force_text(value)
        elif self.value_type == 'bool':
            self.value = force_text(bool(value))
        else:
            self.value = force_text(value)