# Generated by Django 5.2.1 on 2025-06-06 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_document_caption'),
    ]

    operations = [
        migrations.CreateModel(
            name='Correspondent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
