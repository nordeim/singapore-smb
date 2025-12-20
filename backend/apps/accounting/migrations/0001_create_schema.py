"""
Create accounting schema.
"""
from django.db import migrations


class Migration(migrations.Migration):
    """Create PostgreSQL schema for accounting tables."""
    
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.RunSQL(
            sql='CREATE SCHEMA IF NOT EXISTS accounting;',
            reverse_sql='DROP SCHEMA IF EXISTS accounting CASCADE;',
        ),
    ]
