"""
Create compliance schema.

This migration creates the 'compliance' schema in PostgreSQL
if it doesn't already exist (it should exist from the base schema).
"""
from django.db import migrations


class Migration(migrations.Migration):
    
    initial = True
    
    dependencies = [
        ('accounts', '0001_initial'),
    ]
    
    operations = [
        migrations.RunSQL(
            sql='CREATE SCHEMA IF NOT EXISTS compliance;',
            reverse_sql='',  # Don't drop schema on reverse
        ),
    ]
