from django.test import TestCase
from dynamicadmin.models import get_bundle_object, get_dynamic_models, get_dynamic_model, get_dynamic_model_objects
from dynamicadmin.models import BundleEntity, CharField
from django.conf import settings
from django.apps import apps
from django.core.management import call_command


class ContentTest(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.test_app = settings.TESTS_DYNAMIC_APP
        self.test_bundle = apps.get_model(settings.TESTS_BUNDLE_APP, settings.TESTS_BUNDLE_MODEL)

    def setUp(self):
        bundle_model = self.test_bundle.objects.create(name='test_bundle_1', label="test bundle 1")
        charfield = CharField(bundle=bundle_model, name="test_charfield")
        charfield.save()
        bundle_model.fields.add(charfield)

        bundle_model.create_dynamic_model(app_label=self.test_app, base=BundleEntity)
        call_command('makemigrations', '--no-input')
        call_command('migrate')

        dynamic_model = get_bundle_object(self.test_bundle, 'test_bundle_1').get_dynamic_model(self.test_app)
        dynamic_model.objects.create(label="example dynamic model", test_charfield="example content")

    def test_content(self):
        dynamic_model = get_bundle_object(self.test_bundle, 'test_bundle_1').get_dynamic_model(self.test_app)
        new_content = dynamic_model.objects.get(test_charfield="example content")

        self.assertEqual(new_content.test_charfield, "example content")
