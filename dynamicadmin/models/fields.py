import json
from collections import OrderedDict
from json.decoder import JSONDecodeError

from django.contrib.contenttypes.models import ContentType
from django.db import models
from polymorphic.models import PolymorphicModel

from .bundle import Bundle


class Fieldset(models.Model):
    def __str__(self):
        return self.label

    label = models.CharField(max_length=255)
    weight = models.IntegerField(null=True, blank=True)
    classes = models.CharField(max_length=255, blank=True, default='collapse')
    bundle = models.ForeignKey(Bundle, null=False, on_delete=models.CASCADE, related_name='fieldsets', editable=False)


class Field(PolymorphicModel):
    class Meta:
        unique_together = ('bundle', 'name',)

    def __str__(self):
        return self.label

    OPTION_FIELDS = {
        'label': 'verbose_name',
        'help_text': 'help_text',
        'optional': 'blank',
        'nullable': 'null',
        'max_length': 'max_length',
        'on_delete': 'on_delete',
        'related_name': 'related_name',
        'choices': 'choices',
    }

    field_type = None
    name = models.SlugField()
    label = models.CharField(max_length=255)
    weight = models.IntegerField(null=True, blank=True)
    fieldset = models.ForeignKey(Fieldset, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
                                 editable=True)

    help_text = models.TextField(max_length=65535, blank=True)
    optional = models.BooleanField(default=True)

    options = models.TextField(max_length=65535, blank=True, help_text="Extra attributes in JSON dictionary format.")
    bundle = models.ForeignKey(Bundle, null=False, on_delete=models.CASCADE, related_name='fields', editable=False)

    def get_option_fields(self):
        return self.OPTION_FIELDS

    def get_django_field(self):
        django_field = getattr(models, self.field_type, models.CharField)
        if not isinstance(django_field, models.Field):
            # @todo raise
            django_field = models.CharField
        options = self.get_django_field_options()
        if hasattr(self, 'content_type'):
            content_type = getattr(self, 'content_type')
            return django_field(content_type.model_class(), **options)
        return django_field(**options)

    def get_django_field_options(self):
        options = dict()
        for field in self._meta.get_fields():
            field_name = str(field.name)
            value = getattr(self, field_name)
            if field_name in self.get_option_fields():
                option = self.get_option_fields().get(field_name)
                if option == 'on_delete':
                    value = getattr(models, value)
                elif option == 'choices' and len(value):
                    try:
                        value = json.loads(value, object_pairs_hook=OrderedDict)
                    except JSONDecodeError:
                        # @todo raise
                        continue
                    else:
                        if type(value) is not OrderedDict:
                            # @todo raise
                            continue
                        value = list(value.items())
                options[option] = value
            elif field_name == 'options' and len(value):
                try:
                    value = json.loads(value)
                except JSONDecodeError:
                    # @todo raise
                    continue
                else:
                    if type(value) is not dict:
                        # @todo raise
                        continue
                    options.update(value)
        return options


class CharField(Field):
    field_type = models.CharField(max_length=255, default="CharField", editable=False,
                                  choices=(("CharField", "CharField"),))
    choices = models.TextField(max_length=65535, blank=True, help_text="Field choices in JSON dictionary format.")
    max_length = models.IntegerField(default=255)


class TextField(Field):
    field_type = models.CharField(max_length=255, default="TextField", editable=False,
                                  choices=(("TextField", "TextField"),))
    max_length = models.IntegerField(default=65535)


class DateTimeField(Field):
    field_type = models.CharField(max_length=255, default="DateTimeField", editable=False,
                                  choices=(("DateTimeField", "DateTimeField"),))


class URLField(Field):
    field_type = models.CharField(max_length=255, default="URLField", editable=False,
                                  choices=(("URLField", "URLField"),))


class ForeignKeyField(Field):
    field_type = models.CharField(max_length=255, default="ForeignKey", editable=False,
                                  choices=(("ForeignKey", "ForeignKey"),))
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    nullable = models.BooleanField(default=True)
    on_delete = models.CharField(max_length=255, default="DO_NOTHING", editable=True, choices=(
        ("CASCADE", "CASCADE"), ("PROTECT", "PROTECT"), ("SET_NULL", "SET_NULL"), ("SET_DEFAULT", "SET_DEFAULT"),
        ("DO_NOTHING", "DO_NOTHING")))
    related_name = models.CharField(max_length=255, default="+", editable=False)


class ManyToManyField(Field):
    field_type = models.CharField(max_length=255, default="ManyToManyField", editable=False,
                                  choices=(("ManyToManyField", "ManyToManyField"),))
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    related_name = models.CharField(max_length=255, default="+", editable=False)
