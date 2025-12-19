from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql='CREATE SCHEMA IF NOT EXISTS core;',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True, db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('legal_name', models.CharField(max_length=200, blank=True)),
                ('uen', models.CharField(max_length=10, unique=True)),
                ('gst_registered', models.BooleanField(default=False)),
                ('gst_registration_number', models.CharField(max_length=15, blank=True)),
                ('gst_registration_date', models.DateField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('website', models.URLField(blank=True)),
                ('address_line1', models.CharField(max_length=255, blank=True)),
                ('address_line2', models.CharField(max_length=255, blank=True)),
                ('postal_code', models.CharField(max_length=6, blank=True)),
                ('country', models.CharField(max_length=2, default='SG')),
                ('plan_tier', models.CharField(max_length=20, default='lite')),
                ('settings', models.JSONField(default=dict, blank=True)),
            ],
            options={
                'db_table': '"core"."companies"',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('password', models.CharField(max_length=255, db_column='password_hash')),
                ('last_login', models.DateTimeField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100, blank=True)),
                ('last_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('mfa_enabled', models.BooleanField(default=False)),
                ('mfa_secret', models.CharField(max_length=32, blank=True)),
                ('failed_login_attempts', models.PositiveIntegerField(default=0)),
                ('locked_until', models.DateTimeField(null=True, blank=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True, db_index=True)),
                ('company', models.ForeignKey(null=True, blank=True, related_name='users', on_delete=django.db.models.deletion.CASCADE, to='accounts.company')),
            ],
            options={
                'db_table': '"core"."users"',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('permissions', models.JSONField(default=list, blank=True)),
                ('is_system', models.BooleanField(default=False)),
                ('company', models.ForeignKey(null=True, blank=True, related_name='roles', on_delete=django.db.models.deletion.CASCADE, to='accounts.company')),
            ],
            options={
                'db_table': '"core"."roles"',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(null=True, blank=True, related_name='roles_assigned', on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
                ('role', models.ForeignKey(related_name='user_roles', on_delete=django.db.models.deletion.CASCADE, to='accounts.role')),
                ('user', models.ForeignKey(related_name='user_roles', on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
            ],
            options={
                'db_table': '"core"."user_roles"',
            },
        ),
        migrations.AddConstraint(
            model_name='role',
            constraint=models.UniqueConstraint(fields=('company', 'name'), name='unique_role_per_company'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('user', 'role'), name='unique_user_role'),
        ),
    ]
