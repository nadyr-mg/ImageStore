# Generated by Django 3.1.7 on 2021-04-02 09:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(unique=True, upload_to='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('class_id', models.CharField(max_length=255)),
                ('surface', models.JSONField(blank=True, default=list)),
                ('shape', models.JSONField(blank=True, default=dict)),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='core.annotation')),
            ],
        ),
        migrations.AddField(
            model_name='annotation',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.image'),
        ),
    ]
