"""
Initial compliance models migration.

Creates:
- GSTReturn (F5 quarterly filings)
- DataConsent (PDPA consent audit trail)
- DataAccessRequest (PDPA access/deletion requests)
- AuditLog (change tracking)
"""
import uuid
from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    
    dependencies = [
        ('compliance', '0001_create_schema'),
        ('accounts', '0001_initial'),
        ('commerce', '0001_initial'),
    ]
    
    operations = [
        # GSTReturn
        migrations.CreateModel(
            name='GSTReturn',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('quarter', models.IntegerField(
                    choices=[(1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4')]
                )),
                ('year', models.IntegerField()),
                ('box_1', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Standard-rated supplies',
                    max_digits=12
                )),
                ('box_2', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Zero-rated supplies',
                    max_digits=12
                )),
                ('box_3', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Exempt supplies',
                    max_digits=12
                )),
                ('box_4', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Total supplies (computed: 1+2+3)',
                    max_digits=12
                )),
                ('box_5', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Total taxable purchases',
                    max_digits=12
                )),
                ('box_6', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Output tax due',
                    max_digits=12
                )),
                ('box_7', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Input tax claimable',
                    max_digits=12
                )),
                ('box_8', models.DecimalField(
                    decimal_places=2,
                    default=Decimal('0.00'),
                    help_text='Net GST payable/refundable (computed: 6-7)',
                    max_digits=12
                )),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('validated', 'Validated'),
                        ('submitted', 'Submitted'),
                        ('accepted', 'Accepted'),
                        ('rejected', 'Rejected')
                    ],
                    default='draft',
                    max_length=20
                )),
                ('submission_date', models.DateField(blank=True, null=True)),
                ('iras_reference', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='gst_returns',
                    to='accounts.company'
                )),
                ('prepared_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='gst_returns_prepared',
                    to='accounts.user'
                )),
                ('submitted_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='gst_returns_submitted',
                    to='accounts.user'
                )),
            ],
            options={
                'verbose_name': 'GST Return',
                'verbose_name_plural': 'GST Returns',
                'db_table': '"compliance"."gst_returns"',
                'ordering': ['-year', '-quarter'],
                'unique_together': {('company', 'year', 'quarter')},
            },
        ),
        migrations.AddIndex(
            model_name='gstreturn',
            index=models.Index(fields=['company'], name='compliance__company_e0c33f_idx'),
        ),
        migrations.AddIndex(
            model_name='gstreturn',
            index=models.Index(fields=['status'], name='compliance__status_1d4b5e_idx'),
        ),
        
        # DataConsent
        migrations.CreateModel(
            name='DataConsent',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('consent_type', models.CharField(
                    choices=[
                        ('order_processing', 'Order Processing'),
                        ('marketing', 'Marketing'),
                        ('analytics', 'Analytics'),
                        ('third_party', 'Third Party Sharing'),
                        ('profiling', 'Profiling'),
                        ('legal_compliance', 'Legal Compliance')
                    ],
                    max_length=50
                )),
                ('is_granted', models.BooleanField()),
                ('source', models.CharField(
                    blank=True,
                    help_text='Where consent was recorded (registration, checkout, settings)',
                    max_length=50
                )),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('consent_timestamp', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='consent_records',
                    to='commerce.customer'
                )),
            ],
            options={
                'verbose_name': 'Data Consent',
                'verbose_name_plural': 'Data Consents',
                'db_table': '"compliance"."data_consents"',
                'ordering': ['-consent_timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='dataconsent',
            index=models.Index(fields=['customer'], name='compliance__custome_a7b3c2_idx'),
        ),
        
        # DataAccessRequest
        migrations.CreateModel(
            name='DataAccessRequest',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('request_type', models.CharField(
                    choices=[
                        ('access', 'Data Access'),
                        ('correction', 'Data Correction'),
                        ('deletion', 'Data Deletion')
                    ],
                    max_length=20
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('processing', 'Processing'),
                        ('completed', 'Completed'),
                        ('rejected', 'Rejected')
                    ],
                    default='pending',
                    max_length=20
                )),
                ('requested_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('due_date', models.DateField()),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('response_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='data_access_requests',
                    to='accounts.company'
                )),
                ('customer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='data_access_requests',
                    to='commerce.customer'
                )),
                ('processed_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='processed_data_requests',
                    to='accounts.user'
                )),
            ],
            options={
                'verbose_name': 'Data Access Request',
                'verbose_name_plural': 'Data Access Requests',
                'db_table': '"compliance"."data_access_requests"',
                'ordering': ['-requested_at'],
            },
        ),
        migrations.AddIndex(
            model_name='dataaccessrequest',
            index=models.Index(fields=['company'], name='compliance__company_f1d2e3_idx'),
        ),
        migrations.AddIndex(
            model_name='dataaccessrequest',
            index=models.Index(fields=['status'], name='compliance__status_g4h5i6_idx'),
        ),
        
        # AuditLog
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('action', models.CharField(
                    help_text='CREATE, UPDATE, or DELETE',
                    max_length=50
                )),
                ('resource_type', models.CharField(
                    help_text='Model name (e.g., commerce.order)',
                    max_length=50
                )),
                ('resource_id', models.UUIDField(
                    blank=True,
                    help_text='Primary key of the affected resource',
                    null=True
                )),
                ('old_values', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Previous values before change'
                )),
                ('new_values', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='New values after change'
                )),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('company', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='audit_logs',
                    to='accounts.company'
                )),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='audit_logs',
                    to='accounts.user'
                )),
            ],
            options={
                'verbose_name': 'Audit Log',
                'verbose_name_plural': 'Audit Logs',
                'db_table': '"compliance"."audit_logs"',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['company'], name='compliance__company_j7k8l9_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user'], name='compliance__user_id_m0n1o2_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(
                fields=['resource_type', 'resource_id'],
                name='compliance__resourc_p3q4r5_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['created_at'], name='compliance__created_s6t7u8_idx'),
        ),
    ]
