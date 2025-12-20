"""
Initial InvoiceNow migration.

Creates PEPPOL invoice and acknowledgment models.
"""
import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    
    initial = True
    
    dependencies = [
        ('accounting', '0002_initial'),
    ]
    
    operations = [
        # PEPPOLInvoice
        migrations.CreateModel(
            name='PEPPOLInvoice',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('peppol_id', models.CharField(blank=True, max_length=100)),
                ('sender_endpoint', models.CharField(blank=True, max_length=100)),
                ('receiver_endpoint', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('validated', 'Validated'),
                        ('signed', 'Signed'),
                        ('submitted', 'Submitted'),
                        ('acknowledged', 'Acknowledged'),
                        ('rejected', 'Rejected')
                    ],
                    default='draft',
                    max_length=20
                )),
                ('xml_document', models.TextField(blank=True)),
                ('signature_value', models.TextField(blank=True)),
                ('signature_timestamp', models.DateTimeField(blank=True, null=True)),
                ('access_point_provider', models.CharField(blank=True, max_length=100)),
                ('submission_reference', models.CharField(blank=True, max_length=100)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('validation_errors', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='peppol_invoice',
                    to='accounting.invoice'
                )),
            ],
            options={
                'verbose_name': 'PEPPOL Invoice',
                'verbose_name_plural': 'PEPPOL Invoices',
                'db_table': '"compliance"."peppol_invoices"',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='peppolinvoice',
            index=models.Index(fields=['invoice'], name='peppol_invoice_idx'),
        ),
        migrations.AddIndex(
            model_name='peppolinvoice',
            index=models.Index(fields=['status'], name='peppol_status_idx'),
        ),
        
        # PEPPOLAcknowledgment
        migrations.CreateModel(
            name='PEPPOLAcknowledgment',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('acknowledgment_type', models.CharField(
                    choices=[
                        ('delivery', 'Delivery Receipt'),
                        ('application', 'Application Response'),
                        ('error', 'Error Response')
                    ],
                    max_length=20
                )),
                ('message_id', models.CharField(blank=True, max_length=100)),
                ('response_code', models.CharField(blank=True, max_length=20)),
                ('response_description', models.TextField(blank=True)),
                ('response_payload', models.JSONField(blank=True, default=dict)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('peppol_invoice', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='acknowledgments',
                    to='invoicenow.peppolinvoice'
                )),
            ],
            options={
                'verbose_name': 'PEPPOL Acknowledgment',
                'verbose_name_plural': 'PEPPOL Acknowledgments',
                'db_table': '"compliance"."peppol_acknowledgments"',
                'ordering': ['-received_at'],
            },
        ),
    ]
