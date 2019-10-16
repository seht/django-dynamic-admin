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


# import reversion
# from reversion.admin import VersionAdmin


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


def register_content_models(bundle_model, app_label, model_admin=admin.ModelAdmin, base=BundleEntity, **kwargs):
    kwargs['app_label'] = app_label
    kwargs['base'] = base
    bundle_models = bundle_model.objects.all()
    try:
        for bundle_content_model in bundle_models:
            content_model = bundle_content_model.create_django_model(**kwargs)
            # @todo Support reversion.
            # reversion.register(content_model)
            if not admin.site.is_registered(content_model):
                admin.site.register(content_model, model_admin)
    except ProgrammingError:
        pass
    # @todo Optional/custom permissions.
    create_permissions(apps.get_app_config(app_label), verbosity=2)


def unregister_content_models(app_label):
    registry_models = apps.get_app_config(app_label).get_models()
    for model in registry_models:
        admin.site.unregister(model)
    # @see django.apps.registry.register_model
    app_models = apps.all_models[app_label]
    for model_name in app_models.copy():
        model = apps.get_model(app_label, model_name)
        if (model.__name__ == app_models[model_name].__name__ and
                model.__module__ == app_models[model_name].__module__):
            del app_models[model_name]
    apps.clear_cache()


def register_bundle_model(bundle_model, model_admin=BundleAdmin):
    if not admin.site.is_registered(bundle_model):
        admin.site.register(bundle_model, model_admin)


def unregister_bundle_model(model):
    unregister_content_models(model.CONTENT_BUNDLE)


def reload_bundle_models(models=list()):
    for model in models:
        unregister_bundle_model(model)
        register_bundle_model(model)
    # apps.clear_cache()
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()
