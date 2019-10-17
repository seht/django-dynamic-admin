from django.test import TestCase
from dynamicadmin.models import get_bundle_object, get_dynamic_models, get_dynamic_model, get_dynamic_model_objects
from dynamicadmin.models import BundleEntity, CharField
from dynamicadmin.dynamicadmin_tests.models import TestBundle


class ContentTest(TestCase):
    def setUp(self):
        from django.core.management import call_command

        bundle_model = TestBundle.objects.create(name='test_bundle_1', label="test bundle 1")
        charfield = CharField(bundle=bundle_model, name="test_charfield")
        charfield.save()
        bundle_model.fields.add(charfield)

        bundle_model.create_dynamic_model(app_label='dynamicadmin_tests', base=BundleEntity)
        call_command('makemigrations', '--no-input')
        call_command('migrate')

        dynamic_model = get_bundle_object(TestBundle, 'test_bundle_1').get_dynamic_model('dynamicadmin_tests')
        dynamic_model.objects.create(label="example dynamic model", test_charfield="example content")

    def test_content(self):
        dynamic_model = get_bundle_object(TestBundle, 'test_bundle_1').get_dynamic_model('dynamicadmin_tests')
        new_content = dynamic_model.objects.get(test_charfield="example content")

        self.assertEqual(new_content.test_charfield, "example content")
