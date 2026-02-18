# Add status choice 'cancelled' to NegativeLink.
# No schema change: status is a CharField and already accepts any value.
# Safe for existing data; new value is valid from now on.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0003_switch_manager_to_fk'),
    ]

    operations = [
        # Choices are enforced in Python only; no AlterField needed for DB.
    ]
