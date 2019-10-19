# Generated by Django 2.2.6 on 2019-10-19 12:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=255, unique=True)),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('_help_text', models.TextField(blank=True, max_length=650)),
                ('_blank', models.BooleanField(default=True)),
                ('options', models.TextField(blank=True, help_text='Extra attributes in JSON dictionary format.', max_length=65535)),
                ('bundle', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='dynamicadmin.Bundle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_dynamicadmin.field_set+', to='contenttypes.ContentType')),
            ],
            options={
                'unique_together': {('bundle', 'name')},
            },
        ),
        migrations.CreateModel(
            name='CharField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dynamicadmin.Field')),
                ('field_type', models.CharField(choices=[('CharField', 'CharField')], default='CharField', editable=False, max_length=255)),
                ('_max_length', models.IntegerField(default=255)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('dynamicadmin.field',),
        ),
        migrations.CreateModel(
            name='DateTimeField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dynamicadmin.Field')),
                ('field_type', models.CharField(choices=[('DateTimeField', 'DateTimeField')], default='DateTimeField', editable=False, max_length=255)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('dynamicadmin.field',),
        ),
        migrations.CreateModel(
            name='TextField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dynamicadmin.Field')),
                ('field_type', models.CharField(choices=[('TextField', 'TextField')], default='TextField', editable=False, max_length=255)),
                ('_max_length', models.IntegerField(default=65535)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('dynamicadmin.field',),
        ),
        migrations.CreateModel(
            name='URLField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dynamicadmin.Field')),
                ('field_type', models.CharField(choices=[('URLField', 'URLField')], default='URLField', editable=False, max_length=255)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('dynamicadmin.field',),
        ),
        migrations.CreateModel(
            name='ManyToManyField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dynamicadmin.Field')),
                ('field_type', models.CharField(choices=[('ManyToManyField', 'ManyToManyField')], default='ManyToManyField', editable=False, max_length=255)),
                ('_related_name', models.CharField(default='+', editable=False, max_length=255)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('dynamicadmin.field',),
        ),
        migrations.CreateModel(
            name='ForeignKeyField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dynamicadmin.Field')),
                ('field_type', models.CharField(choices=[('ForeignKey', 'ForeignKey')], default='ForeignKey', editable=False, max_length=255)),
                ('_null', models.BooleanField(default=True)),
                ('_on_delete', models.CharField(choices=[('CASCADE', 'CASCADE'), ('PROTECT', 'PROTECT'), ('SET_NULL', 'SET_NULL'), ('SET_DEFAULT', 'SET_DEFAULT'), ('DO_NOTHING', 'DO_NOTHING')], default='DO_NOTHING', max_length=255)),
                ('_related_name', models.CharField(default='+', editable=False, max_length=255)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('dynamicadmin.field',),
        ),
    ]
