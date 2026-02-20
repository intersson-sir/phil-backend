from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0005_add_account_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='negativelink',
            name='platform',
            field=models.CharField(
                choices=[
                    ('facebook', 'Facebook'),
                    ('twitter', 'Twitter'),
                    ('youtube', 'YouTube'),
                    ('reddit', 'Reddit'),
                    ('account', 'Account'),
                    ('other', 'Other'),
                ],
                help_text='Platform where the content is hosted',
                max_length=20,
            ),
        ),
    ]
