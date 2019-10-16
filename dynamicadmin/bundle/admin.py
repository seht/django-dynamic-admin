from importlib import reload
from django.contrib import admin
from django.apps import apps
from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db.utils import ProgrammingError
from django.urls.base import clear_url_caches
from django.utils.module_loading import import_module

from dynamicadmin.entity.models import BundleEntity
from .models import CharField, TextField, TaxonomyDictionaryField, DateTimeField, URLField


class BundleAdmin(admin.ModelAdmin):

    class BundleTabularInline(admin.TabularInline):
        show_change_link = True
        extra = 0

    class CharFieldInline(BundleTabularInline):
        model = CharField

    class TextFieldInline(BundleTabularInline):
        model = TextField

    class DateTimeFieldInline(BundleTabularInline):
        model = DateTimeField

    class URLFieldInline(BundleTabularInline):
        model = URLField

    class TaxonomyListFieldInline(BundleTabularInline):
        model = TaxonomyDictionaryField

    inlines = [
        CharFieldInline,
        TextFieldInline,
        DateTimeFieldInline,
        URLFieldInline,
        TaxonomyListFieldInline,
    ]


def get_bundle_objects(bundle_model):
    return bundle_model.objects.all()


def register_bundle_model(bundle_model, model_admin=BundleAdmin):
    if not admin.site.is_registered(bundle_model):
        admin.site.register(bundle_model, model_admin)


def unregister_bundle_model(bundle_model):
    if admin.site.is_registered(bundle_model):
        admin.site.unregister(bundle_model)


# def reload_bundle_models(models=list()):
#     for model in models:
#         unregister_bundle_model(model)
#         register_bundle_model(model)
#     reload(import_module(settings.ROOT_URLCONF))
#     clear_url_caches()


def get_dynamic_models(app_label):
    return apps.get_app_config(app_label).get_models()


def register_dynamic_model(bundle_model_object, model_admin=admin.ModelAdmin, **kwargs):
    dynamic_model = bundle_model_object.create_django_model(**kwargs)
    if not admin.site.is_registered(dynamic_model):
        admin.site.register(dynamic_model, model_admin)


def register_dynamic_models(bundle_model, app_label, model_admin=admin.ModelAdmin, base=BundleEntity, **kwargs):
    kwargs['app_label'] = app_label
    kwargs['base'] = base
    bundle_models_objects = get_bundle_objects(bundle_model)
    for bundle_model_object in bundle_models_objects:
        register_dynamic_model(bundle_model_object, model_admin=model_admin, **kwargs)


# @see django.apps.registry.register_model
def unregister_dynamic_models(app_label):
    for dynamic_model in get_dynamic_models(app_label):
        admin.site.unregister(dynamic_model)
    app_models = apps.all_models[app_label]
    for model_name in app_models.copy():
        model = apps.get_model(app_label, model_name)
        if (model.__name__ == app_models[model_name].__name__ and
                model.__module__ == app_models[model_name].__module__):
            del app_models[model_name]
    apps.clear_cache()


def create_dynamic_model_permissions(verbosity=2):
    create_permissions(apps.get_app_config(app_label), verbosity=verbosity)
