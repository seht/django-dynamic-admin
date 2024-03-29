# from collections import OrderedDict
# from importlib import reload
# from django.conf import settings
# from django.urls.base import clear_url_caches
# from django.utils.module_loading import import_module
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.management import create_permissions
from django.db.utils import ProgrammingError
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline

from .models.bundle import get_dynamic_models, get_bundle_objects
from .models.fields import *


class FieldAdminInline(StackedPolymorphicInline):
    class FieldAdminInlineChild(StackedPolymorphicInline.Child):
        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "fieldset":
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    bundle=request.resolver_match.kwargs.get('object_id'))
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        extra = 0
        classes = ("collapse",)

    # @todo dynamic inlines
    class CharFieldInline(FieldAdminInlineChild):
        model = CharField

    class TextFieldInline(FieldAdminInlineChild):
        model = TextField

    class DateTimeFieldInline(FieldAdminInlineChild):
        model = DateTimeField

    class URLFieldInline(FieldAdminInlineChild):
        model = URLField

    class ForeignKeyFieldInline(FieldAdminInlineChild):
        model = ForeignKeyField

    class ManyToManyFieldInline(FieldAdminInlineChild):
        model = ManyToManyField

    model = Field

    child_inlines = (
        CharFieldInline,
        TextFieldInline,
        DateTimeFieldInline,
        URLFieldInline,
        ForeignKeyFieldInline,
        ManyToManyFieldInline,
    )

    extra = 0
    # classes = ("collapse",)


class FieldsetsetAdminInline(admin.TabularInline):
    model = Fieldset

    extra = 0
    classes = ("collapse",)


class BundleAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (FieldsetsetAdminInline, FieldAdminInline,)


class DynamicModelAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # @todo fieldsets, field order
        # print(self.fields)
        # print(self.fieldsets)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


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


def register_dynamic_model(bundle_model_object, model_admin=admin.ModelAdmin, **kwargs):
    dynamic_model = bundle_model_object.create_dynamic_model(**kwargs)
    if not admin.site.is_registered(dynamic_model):
        admin.site.register(dynamic_model, model_admin)


def register_dynamic_models(bundle_model, app_label, model_admin=admin.ModelAdmin, base=models.Model, **kwargs):
    try:
        bundle_models_objects = list(get_bundle_objects(bundle_model))
    except ProgrammingError:
        # Before bundle models have been migrated.
        pass
    else:
        kwargs['app_label'] = app_label
        kwargs['base'] = base
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


def create_dynamic_model_permissions(app_label, verbosity=2):
    create_permissions(apps.get_app_config(app_label), verbosity=verbosity)
