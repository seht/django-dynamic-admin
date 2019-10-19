import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models
from polymorphic.models import PolymorphicModel


# @see https://code.djangoproject.com/wiki/DynamicModels
def dynamic_model_factory(name, fields, base=models.Model, module=None, **kwargs):
    if not module:
        module = base.__module__

    class Meta:
        pass

    for key, value in dict(kwargs).items():
        setattr(Meta, key, value)

    attrs = {
        '__module__': module,
        'Meta': Meta,
    }

    if fields:
        attrs.update(fields)

    model = type(name, (base,), attrs)

    return model


def get_bundle_model(app_label, model_name):
    return apps.get_app_config(app_label).get_model(model_name=model_name)


def get_bundle_object(bundle_model, object_name):
    return bundle_model.objects.get(name=object_name)


def get_bundle_objects(bundle_model, **kwargs):
    return bundle_model.objects.filter(**kwargs)


def get_dynamic_models(app_label):
    return apps.get_app_config(app_label).get_models()


def get_dynamic_model(app_label, model_name):
    return apps.get_app_config(app_label).get_model(model_name=model_name)


def get_dynamic_model_objects(dynamic_model, **kwargs):
    return dynamic_model.objects.filter(**kwargs)


class Bundle(models.Model):
    def __str__(self):
        return self.label

    ATTRIBUTE_FIELDS = {
        'label': 'verbose_name',
    }

    objects = models.Manager()
    fields = None

    name = models.SlugField(max_length=255, unique=True)
    label = models.CharField(max_length=255)

    def get_attribute_fields(self):
        return self.ATTRIBUTE_FIELDS

    def get_dynamic_model(self, app_label):
        return get_dynamic_model(app_label, model_name=self.name)

    def create_dynamic_model(self, **kwargs):
        fields = self.get_django_model_fields()
        fields.append(('bundle', models.ForeignKey(self, default=self.pk, related_name='+', on_delete=models.PROTECT,
                                                   editable=False)))
        kwargs = dict(kwargs)
        kwargs.update(self.get_django_model_attributes())
        return dynamic_model_factory(self.name, fields, **kwargs)

    def get_django_model_fields(self):
        return list((field.name, field.get_django_field()) for field in self.fields.all())

    def get_django_model_attributes(self):
        attributes = dict()
        for field in self._meta.get_fields():
            field_name = str(field.name)
            value = getattr(self, field_name)
            if field_name in self.get_attribute_fields():
                attribute = self.get_attribute_fields().get(field_name)
                attributes[attribute] = value
        return attributes


# @todo
def dynamic_field_factory(field_type, content_type=None, module=None, weight=1, **attributes):
    base = getattr(models, field_type)

    class BundleFieldEntity(base):
        def __init__(self, *args):
            self.weight = weight
            super().__init__(*args, **attributes)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs['weight'] = self.weight
            return name, path, args, kwargs

    field = type(field_type, (BundleFieldEntity,), {})

    if content_type:
        return field(content_type, **attributes)
    return field(**attributes)


class Field(PolymorphicModel):
    class Meta:
        unique_together = ('bundle', 'name',)

    def __str__(self):
        return self.label

    ATTRIBUTE_FIELDS = {
        'label': 'verbose_name',
        'help_text': 'help_text',
        'optional': 'blank',
        'nullable': 'null',
        'max_length': 'max_length',
        'on_delete': 'on_delete',
        'related_name': 'related_name',
    }

    field_type = None
    name = models.SlugField(max_length=255)
    label = models.CharField(max_length=255)
    weight = models.IntegerField(null=True, blank=True)

    help_text = models.TextField(max_length=650, blank=True)
    optional = models.BooleanField(default=True)

    options = models.TextField(max_length=65535, blank=True, help_text="Extra attributes in JSON dictionary format.")
    bundle = models.ForeignKey(Bundle, null=False, on_delete=models.CASCADE, related_name='fields', editable=False)

    def get_attribute_fields(self):
        return self.ATTRIBUTE_FIELDS

    def get_django_field(self):
        # @todo except
        django_field = getattr(models, self.field_type)
        attributes = self.get_django_field_attributes()
        if hasattr(self, 'content_type'):
            related_model = getattr(self, 'content_type')
            return django_field(related_model.model_class(), **attributes)
        return django_field(**attributes)

    def get_django_field_attributes(self):
        attributes = dict()
        for field in self._meta.get_fields():
            field_name = str(field.name)
            value = getattr(self, field_name)
            if field_name in self.get_attribute_fields():
                attribute = self.get_attribute_fields().get(field_name)
                if attribute == 'on_delete':
                    value = getattr(models, value)
                attributes[attribute] = value
            elif field_name == 'options' and len(value):
                # @todo validate options
                options = dict(json.loads(value))
                attributes.update(options)
        return attributes


class CharField(Field):
    field_type = models.CharField(max_length=255, default="CharField", editable=False,
                                  choices=(("CharField", "CharField"),))
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
