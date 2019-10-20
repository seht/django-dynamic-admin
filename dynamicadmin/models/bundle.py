# from collections import OrderedDict
from django.apps import apps
from django.db import models


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


def get_bundle_object(bundle_model, **kwargs):
    return bundle_model.objects.get(**kwargs)


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
    fieldsets = None

    name = models.SlugField(unique=True)
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
