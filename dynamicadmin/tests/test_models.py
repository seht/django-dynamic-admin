from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.test import TestCase

from dynamicadmin.models import CharField
from dynamicadmin.models import get_bundle_object


class DynamicModelTest(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.test_app = settings.TESTS_DYNAMIC_APP
        self.test_bundle = apps.get_model(settings.TESTS_BUNDLE_APP, settings.TESTS_BUNDLE_MODEL)

    def setUp(self):
        bundle_model = self.test_bundle.objects.create(name='test_bundle', label="test bundle")
        test_charfield = CharField(bundle=bundle_model, name="test_charfield")
        test_options = CharField(bundle=bundle_model, name="test_options", options='{"default": "default value"}')
        test_charfield.save()
        test_options.save()
        bundle_model.fields.add(test_charfield)
        bundle_model.fields.add(test_options)

        bundle_model.create_dynamic_model(app_label=self.test_app, base=models.Model)
        call_command('makemigrations', '--no-input')
        call_command('migrate')

        dynamic_model = get_bundle_object(self.test_bundle, 'test_bundle').get_dynamic_model(self.test_app)
        dynamic_model.objects.create(test_charfield="example content")

    def test_content(self):
        dynamic_model = get_bundle_object(self.test_bundle, 'test_bundle').get_dynamic_model(self.test_app)
        new_content = dynamic_model.objects.get(test_charfield="example content")

        self.assertEqual(new_content.test_charfield, "example content")
        self.assertEqual(new_content.test_options, "default value")
