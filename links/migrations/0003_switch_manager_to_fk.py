# Remove legacy manager (CharField), rename manager_fk -> manager

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0002_populate_manager_fk'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='negativelink',
            name='links_negat_manager_77ed11_idx',
        ),
        migrations.RemoveField(
            model_name='negativelink',
            name='manager',
        ),
        migrations.RenameField(
            model_name='negativelink',
            old_name='manager_fk',
            new_name='manager',
        ),
    ]
