from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.test import TestCase
from dynamicadmin.models.fields import CharField
from dynamicadmin.models.bundle import get_bundle_object


class DynamicModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_app = settings.TESTS_DYNAMIC_APP
        test_bundle = apps.get_model(settings.TESTS_BUNDLE_APP, settings.TESTS_BUNDLE_MODEL)

        bundle_model = test_bundle.objects.create(name='test_bundle', label="test bundle")

        CharField.objects.create(bundle=bundle_model, name="test_charfield", label='test charfield')
        CharField.objects.create(bundle=bundle_model, name="test_options", label='test options',
                                 options='{"default": "default value"}')

        bundle_model.create_dynamic_model(app_label=test_app, base=models.Model)

        call_command('makemigrations', '--no-input')
        call_command('migrate')

        cls.dynamic_model = get_bundle_object(test_bundle, name='test_bundle').get_dynamic_model(test_app)
        cls.dynamic_model.objects.create(test_charfield="example content")

    def test_charfield(self):
        content = self.dynamic_model.objects.get(test_charfield="example content")
        self.assertEqual(content.test_charfield, "example content")

    def test_field_options(self):
        content = self.dynamic_model.objects.get(test_options="default value")
        self.assertEqual(content.test_options, "default value")
