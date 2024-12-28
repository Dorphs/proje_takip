from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gorev',
            old_name='ad',
            new_name='baslik',
        ),
        migrations.RenameField(
            model_name='gorev',
            old_name='sorumlu',
            new_name='atanan',
        ),
        migrations.RemoveField(
            model_name='gorev',
            name='baslama_tarihi',
        ),
        migrations.RemoveField(
            model_name='gorev',
            name='bitis_tarihi',
        ),
        migrations.RemoveField(
            model_name='gorev',
            name='oncelik',
        ),
        migrations.AddField(
            model_name='gorev',
            name='son_tarih',
            field=models.DateField(blank=True, null=True),
        ),
    ]
