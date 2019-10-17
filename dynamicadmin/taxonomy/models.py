from django.db import models
from polymorphic.models import PolymorphicModel
from dynamicadmin.entity.models import TaxonomyDictionaryEntity, TaxonomyEntity
from dynamicadmin.apps import DynamicadminConfig


class TaxonomyDictionary(TaxonomyDictionaryEntity, PolymorphicModel):
    class Meta:
        app_label = DynamicadminConfig.name


class TaxonomyTerm(TaxonomyEntity):
    class Meta:
        app_label = DynamicadminConfig.name

    dictionary = models.ForeignKey(TaxonomyDictionary, null=True, on_delete=models.CASCADE, related_name='terms')
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, editable=False)
