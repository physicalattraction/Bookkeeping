# Generated by Django 2.1.7 on 2019-03-10 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('uuid', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('account', models.CharField(help_text='Bank account of the contact', max_length=64)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
