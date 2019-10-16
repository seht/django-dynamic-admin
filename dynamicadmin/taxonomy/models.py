from django.db import models
from polymorphic.models import PolymorphicModel
from dynamicadmin.entity.models import TaxonomyDictionaryEntity, TaxonomyEntity


class TaxonomyDictionary(TaxonomyDictionaryEntity, PolymorphicModel):
    class Meta:
        app_label = 'dynamicadmin'


class TaxonomyTerm(TaxonomyEntity):
    class Meta:
        app_label = 'dynamicadmin'

    dictionary = models.ForeignKey(TaxonomyDictionary, null=True, on_delete=models.CASCADE, related_name='terms')
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, editable=False)
