from django.db import models
from inspect import signature, getmro
from django.apps import apps
from polymorphic.models import PolymorphicModel
from dynamicadmin.entity.models import NamedEntity, UniqueNamedEntity, TaxonomyEntity
from dynamicadmin.taxonomy.models import TaxonomyDictionary, TaxonomyTerm
from dynamicadmin.apps import DynamicadminConfig


# @see https://code.djangoproject.com/wiki/DynamicModels
def dynamic_model_factory(name, label, fields, app_label, module=None, base=models.Model):
    if not module:
        module = base.__module__

    class Meta:
        pass

    setattr(Meta, 'app_label', app_label)
    setattr(Meta, 'verbose_name', label)
    setattr(Meta, 'verbose_name_plural', label)

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
    return bundle_model.objects.fitler(**kwargs)


def get_dynamic_models(app_label):
    return apps.get_app_config(app_label).get_models()


def get_dynamic_model(app_label, model_name):
    return apps.get_app_config(app_label).get_model(model_name=model_name)


def get_dynamic_model_objects(dynamic_model, **kwargs):
    return dynamic_model.objects.filter(**kwargs)


class Bundle(UniqueNamedEntity, TaxonomyEntity):
    class Meta:
        app_label = DynamicadminConfig.name

    objects = models.Manager()
    dynamic_model_app_label = ''

    def create_dynamic_model(self, **kwargs):
        fields = self.get_dynamic_model_fields()
        fields.append(('bundle',
                       models.ForeignKey(self, default=self.pk, editable=False, on_delete=models.DO_NOTHING,
                                         related_name='+')))
        self.dynamic_model_app_label = kwargs.get('app_label')
        return dynamic_model_factory(self.name, self.label, dict(fields), **kwargs)

    def get_dynamic_model(self, app_label):
        return get_dynamic_model(app_label, model_name=self.name)

    def get_dynamic_model_fields(self):
        return [(field.name, field.get_django_field()) for field in self.fields.all()]


class Field(NamedEntity, TaxonomyEntity, PolymorphicModel):
    class Meta:
        app_label = DynamicadminConfig.name
        unique_together = ('bundle', 'name',)

    def __str__(self):
        return self.label

    bundle = models.ForeignKey(Bundle, null=True, on_delete=models.CASCADE, related_name='fields')
    help_text = models.TextField(max_length=650, blank=True)
    required = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)

    def get_django_field(self):
        settings = self.get_django_field_settings()
        field_type = self.type
        if field_type == "ForeignKey":
            content_type = self.content_type
            settings['related_name'] = "+"
            if self.multiple:
                field_type = "ManyToManyField"
            else:
                settings['null'] = True
                settings['on_delete'] = models.DO_NOTHING
            if isinstance(content_type, TaxonomyDictionary):
                settings['limit_choices_to'] = {'dictionary': content_type.pk}
                content_type = TaxonomyTerm
            return getattr(models, field_type)(content_type, **dict(settings))
        return getattr(models, field_type)(**dict(settings))

    # Get base keyword attributes.
    def get_django_field_attributes(self):
        attributes = []
        for base in getmro(getattr(models, self.type)):
            attributes.extend(signature(base).parameters.keys())
        return attributes

    # Match base keyword attributes with field attributes.
    def get_django_field_settings(self):
        settings = {}
        attributes = self.get_django_field_attributes()
        for field in self._meta.get_fields():
            value = getattr(self, field.name)
            if field.name in attributes:
                settings[field.name] = value
        if not getattr(self, 'required'):
            settings['blank'] = True
        settings['verbose_name'] = self.label
        settings['help_text'] = self.help_text
        return settings


class CharField(Field):
    type = models.CharField(max_length=255, default="CharField", editable=False)
    max_length = models.IntegerField(default=255)
    default = models.CharField(max_length=255, blank=True)


class TextField(Field):
    type = models.CharField(max_length=255, default="TextField", editable=False)
    max_length = models.IntegerField(default=65535)
    default = models.TextField(max_length=65535, blank=True)


class DateTimeField(Field):
    type = models.CharField(max_length=255, default="DateTimeField", editable=False)
    default = models.DateTimeField(null=True, blank=True)


class URLField(Field):
    type = models.CharField(max_length=255, default="URLField", editable=False)
    default = models.URLField(max_length=255, blank=True)


class TaxonomyDictionaryField(Field):
    type = models.CharField(max_length=255, default="ForeignKey", editable=False)
    content_type = models.ForeignKey(TaxonomyDictionary, null=True, on_delete=models.DO_NOTHING)
