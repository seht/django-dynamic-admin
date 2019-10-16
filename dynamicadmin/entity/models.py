from django.db import models


class LabeledEntity(models.Model):
    def __str__(self):
        return self.label

    class Meta:
        abstract = True

    label = models.CharField(max_length=255)


class NamedEntity(models.Model):
    class Meta:
        abstract = True

    name = models.SlugField(max_length=255)


class UniqueNamedEntity(models.Model):
    class Meta:
        abstract = True

    name = models.SlugField(max_length=255, unique=True)


class SortableEntity(models.Model):
    class Meta:
        abstract = True

    weight = models.IntegerField(null=True, blank=True)


class TaxonomyEntity(LabeledEntity, SortableEntity):
    class Meta:
        abstract = True


class TaxonomyDictionaryEntity(TaxonomyEntity, UniqueNamedEntity):
    class Meta:
        abstract = True


class BundleEntity(TaxonomyEntity):
    class Meta:
        abstract = True
