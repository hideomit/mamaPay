from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_title_rank_total_earned_coin'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE title_rank DROP COLUMN IF EXISTS display_order;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
