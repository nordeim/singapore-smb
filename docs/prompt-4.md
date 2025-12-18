## 7. COMPLIANCE & REGULATORY FRAMEWORK

### 7.1 GST Compliance Requirements

#### 7.1.1 GST Registration & Monitoring
```python
class GSTComplianceManager:
    """Comprehensive GST compliance management system"""
    
    def __init__(self, company):
        self.company = company
        self.current_rate = Decimal('0.09')  # 9% as of 2024
        self.registration_threshold = Decimal('1000000')  # SGD annual turnover
        self.filing_frequency = 'quarterly'  # IRAS requirement
        self.filing_deadline_days = 30  # Days after quarter end
        
    def monitor_registration_requirement(self):
        """Monitor if GST registration is required based on rolling 12-month revenue"""
        
        # Calculate rolling 12-month revenue
        rolling_revenue = self.calculate_rolling_12_month_revenue()
        
        # Get current GST registration status
        current_status = self.company.gst_registration_status
        
        # Check threshold proximity
        if rolling_revenue >= self.registration_threshold * Decimal('0.9'):
            # 90% of threshold reached - send warning alert
            self.send_threshold_warning(rolling_revenue)
        
        if rolling_revenue >= self.registration_threshold:
            if current_status != 'registered':
                # Above threshold but not registered - critical alert
                self.send_registration_required_alert(rolling_revenue)
        else:
            if current_status == 'registered':
                # Below threshold but registered - check if eligible for deregistration
                self.check_deregistration_eligibility(rolling_revenue)
    
    def prepare_gst_f5_return(self, quarter, year):
        """Prepare GST F5 return for IRAS submission"""
        
        # Validate quarter and year
        if quarter not in [1, 2, 3, 4]:
            raise ValueError("Invalid quarter number")
        
        # Calculate period dates
        period_start, period_end = self.get_quarter_dates(quarter, year)
        
        # Get all taxable transactions in period
        sales = self.get_taxable_sales(period_start, period_end)
        purchases = self.get_taxable_purchases(period_start, period_end)
        
        # Calculate F5 boxes
        f5_data = {
            # Box 1: Total value of standard-rated supplies
            'box_1': self.calculate_standard_rated_supplies(sales),
            
            # Box 2: Total value of zero-rated supplies
            'box_2': self.calculate_zero_rated_supplies(sales),
            
            # Box 3: Total value of exempt supplies
            'box_3': self.calculate_exempt_supplies(sales),
            
            # Box 4: Total value of all supplies (Box 1 + Box 2 + Box 3)
            'box_4': self.calculate_total_supplies(sales),
            
            # Box 5: Total value of taxable purchases (standard-rated + zero-rated)
            'box_5': self.calculate_taxable_purchases(purchases),
            
            # Box 6: Total output tax (GST charged on sales)
            'box_6': self.calculate_output_tax(sales),
            
            # Box 7: Total input tax (GST paid on purchases)
            'box_7': self.calculate_input_tax(purchases),
            
            # Box 8: Net GST payable/refundable (Box 6 - Box 7)
            'box_8': self.calculate_net_gst(sales, purchases),
        }
        
        # Validate F5 data integrity
        self.validate_f5_data_integrity(f5_data)
        
        # Create F5 return record
        f5_return = GSTF5Return.objects.create(
            company=self.company,
            quarter=quarter,
            year=year,
            period_start=period_start,
            period_end=period_end,
            box_1=f5_data['box_1'],
            box_2=f5_data['box_2'],
            box_3=f5_data['box_3'],
            box_4=f5_data['box_4'],
            box_5=f5_data['box_5'],
            box_6=f5_data['box_6'],
            box_7=f5_data['box_7'],
            box_8=f5_data['box_8'],
            status='draft',
            prepared_by=self.company.gst_preparer
        )
        
        return f5_return
    
    def validate_f5_data_integrity(self, f5_data):
        """Validate F5 data integrity before submission"""
        
        validation_errors = []
        
        # Box 4 should equal Box 1 + Box 2 + Box 3
        if abs(f5_data['box_4'] - (f5_data['box_1'] + f5_data['box_2'] + f5_data['box_3'])) > Decimal('0.01'):
            validation_errors.append("Box 4 does not equal sum of Box 1, Box 2, and Box 3")
        
        # Box 5 should be greater than or equal to Box 7 (input tax cannot exceed taxable purchases)
        if f5_data['box_7'] > f5_data['box_5'] + Decimal('0.01'):
            validation_errors.append("Input tax (Box 7) cannot exceed taxable purchases (Box 5)")
        
        # Net GST should be reasonable (not excessive positive or negative)
        if abs(f5_data['box_8']) > Decimal('1000000'):  # S$1 million threshold
            validation_errors.append("Net GST amount appears unreasonably large")
        
        # Check for zero values that might indicate missing data
        zero_value_boxes = [box for box, value in f5_data.items() if box.startswith('box_') and value == 0]
        if zero_value_boxes and len(zero_value_boxes) > 3:
            validation_errors.append(f"Multiple zero-value boxes detected: {', '.join(zero_value_boxes)}")
        
        if validation_errors:
            raise GSTValidationError(f"F5 data validation failed: {', '.join(validation_errors)}")
        
        return True
    
    def submit_gst_return(self, f5_return):
        """Submit GST return to IRAS via myTax Portal integration"""
        
        # Validate return is ready for submission
        if f5_return.status != 'validated':
            raise GSTSubmissionError("GST return must be validated before submission")
        
        # Prepare submission data
        submission_data = {
            'uen': self.company.uen,
            'gst_reg_no': self.company.gst_registration_number,
            'quarter': f5_return.quarter,
            'year': f5_return.year,
            'box_1': str(f5_return.box_1),
            'box_2': str(f5_return.box_2),
            'box_3': str(f5_return.box_3),
            'box_4': str(f5_return.box_4),
            'box_5': str(f5_return.box_5),
            'box_6': str(f5_return.box_6),
            'box_7': str(f5_return.box_7),
            'box_8': str(f5_return.box_8),
            'declaration': True,
            'digital_signature': self.get_digital_signature()
        }
        
        # Submit to IRAS API
        try:
            iras_response = IRASAPI.submit_gst_return(submission_data)
            
            if iras_response['success']:
                # Update return status
                f5_return.status = 'submitted'
                f5_return.submission_date = timezone.now()
                f5_return.transaction_id = iras_response['transaction_id']
                f5_return.receipt_number = iras_response['receipt_number']
                f5_return.save()
                
                # Update company GST status
                self.update_company_gst_status()
                
                # Schedule payment if GST payable
                if f5_return.box_8 > 0:
                    self.schedule_gst_payment(f5_return)
                
                return {
                    'success': True,
                    'transaction_id': iras_response['transaction_id'],
                    'receipt_number': iras_response['receipt_number'],
                    'submission_date': timezone.now()
                }
            else:
                raise GSTSubmissionError(f"IRAS submission failed: {iras_response['error']}")
        
        except Exception as e:
            logger.error(f"GST submission error: {str(e)}", exc_info=True)
            raise GSTSubmissionError(f"Failed to submit GST return: {str(e)}")

    def generate_supporting_documents(self, f5_return):
        """Generate supporting documents required for GST audit"""
        
        documents = {
            'f7_detailed_breakdown': self.generate_f7_detailed_breakdown(f5_return),
            'sales_register': self.generate_sales_register(f5_return),
            'purchase_register': self.generate_purchase_register(f5_return),
            'zero_rated_export_proof': self.generate_export_proof(f5_return),
            'input_tax_claim_proof': self.generate_input_tax_proof(f5_return),
            'bad_debt_relief_documentation': self.generate_bad_debt_documentation(f5_return)
        }
        
        # Store documents in secure storage
        for doc_name, doc_content in documents.items():
            self.store_supporting_document(f5_return, doc_name, doc_content)
        
        return documents
```

#### 7.1.2 InvoiceNow Integration (PEPPOL Compliance)
```python
def generate_peppol_invoice(order):
    """Generate PEPPOL-compliant e-invoice for InvoiceNow"""
    
    # Validate order has required fields for PEPPOL
    if not order.company.uen or not order.company.gst_registration_number:
        raise InvoiceGenerationError("Company missing required PEPPOL fields (UEN, GST reg number)")
    
    if not order.customer.uen and not order.customer.overseas_customer:
        raise InvoiceGenerationError("Customer missing UEN for domestic transactions")
    
    # Generate invoice number (sequential with company prefix)
    invoice_number = generate_sequential_invoice_number(order.company)
    
    # Prepare PEPPOL invoice structure
    invoice = {
        'header': {
            'invoice_number': invoice_number,
            'issue_date': order.created_at.date().isoformat(),
            'due_date': (order.created_at + timedelta(days=30)).date().isoformat(),
            'currency': 'SGD',
            'document_type': '380',  # Commercial invoice
            'invoice_type_code': '380'
        },
        'supplier': {
            'uen': order.company.uen,
            'name': order.company.name,
            'gst_reg_no': order.company.gst_registration_number,
            'address': order.company.registered_address,
            'postal_code': order.company.postal_code,
            'country': 'SG',
            'contact_person': order.company.contact_person,
            'contact_email': order.company.contact_email,
            'contact_phone': order.company.contact_phone,
            'endpoint_id': order.company.peppol_endpoint_id  # PEPPOL endpoint ID
        },
        'customer': {
            'uen': order.customer.uen or '',
            'name': order.customer.name,
            'address': order.customer.billing_address,
            'postal_code': order.customer.postal_code,
            'country': order.customer.country_code,
            'contact_person': order.customer.contact_person,
            'contact_email': order.customer.contact_email,
            'contact_phone': order.customer.contact_phone,
            'endpoint_id': order.customer.peppol_endpoint_id or ''
        },
        'line_items': [],
        'tax_breakdown': {
            'taxable_amount': order.subtotal,
            'tax_rate': float(order.gst_rate),
            'tax_amount': order.gst_amount,
            'total_amount': order.total_amount
        },
        'legal_monetary_totals': {
            'line_extension_amount': order.subtotal,
            'tax_exclusive_amount': order.subtotal,
            'tax_inclusive_amount': order.total_amount,
            'allowance_total_amount': order.discount_amount,
            'charge_total_amount': order.shipping_amount,
            'prepaid_amount': order.amount_paid,
            'payable_amount': order.total_amount - order.amount_paid
        },
        'payment_means': {
            'payment_means_code': '31',  # Credit transfer
            'payment_id': order.order_number,
            'payee_account': {
                'account_id': order.company.bank_account_number,
                'account_name': order.company.bank_account_name,
                'financial_institution_branch_id': order.company.bank_code
            }
        }
    }
    
    # Add line items
    for item in order.items.all():
        line_item = {
            'line_id': str(item.id),
            'invoiced_quantity': item.quantity,
            'unit_code': 'EA',  # Each
            'unit_price': item.unit_price,
            'line_extension_amount': item.total_price,
            'description': item.product.name,
            'tax_category_code': get_tax_category_code(item.product.gst_type),
            'tax_rate': float(item.product.gst_rate),
            'item_name': item.product.name,
            'item_description': item.product.description,
            'seller_item_id': item.product.sku,
            'standard_item_id': item.product.sku  # Using SKU as standard ID
        }
        invoice['line_items'].append(line_item)
    
    # Add allowances (discounts)
    if order.discount_amount > 0:
        invoice['allowances'] = [{
            'charge_indicator': False,
            'allowance_charge_reason': 'Discount',
            'amount': order.discount_amount,
            'base_amount': order.subtotal,
            'percentage': (order.discount_amount / order.subtotal * 100) if order.subtotal > 0 else 0,
            'tax_category_code': get_tax_category_code(order.items.first().product.gst_type),
            'tax_rate': float(order.gst_rate)
        }]
    
    # Add charges (shipping)
    if order.shipping_amount > 0:
        invoice['charges'] = [{
            'charge_indicator': True,
            'allowance_charge_reason': 'Shipping',
            'amount': order.shipping_amount,
            'base_amount': order.subtotal,
            'percentage': (order.shipping_amount / order.subtotal * 100) if order.subtotal > 0 else 0,
            'tax_category_code': get_tax_category_code(order.items.first().product.gst_type),
            'tax_rate': float(order.gst_rate)
        }]
    
    # Add delivery information
    if order.shipping_address:
        invoice['delivery'] = {
            'actual_delivery_date': order.estimated_delivery_date.isoformat() if order.estimated_delivery_date else None,
            'delivery_address': {
                'street_name': order.shipping_address,
                'city_name': 'Singapore',
                'postal_zone': order.shipping_postal_code,
                'country_subentity': '',
                'country': 'SG'
            }
        }
    
    # Add tax representative if applicable
    if order.company.tax_representative:
        invoice['tax_representative'] = {
            'name': order.company.tax_representative.name,
            'registration_number': order.company.tax_representative.registration_number
        }
    
    # Validate PEPPOL compliance
    validate_peppol_compliance(invoice)
    
    return invoice

def submit_to_invoicenow(invoice_data):
    """Submit PEPPOL invoice to InvoiceNow via Access Point Provider"""
    
    # Get company's Access Point Provider configuration
    app_config = get_app_configuration(invoice_data['supplier']['uen'])
    
    if not app_config:
        raise InvoiceSubmissionError("Company not configured with Access Point Provider")
    
    # Prepare PEPPOL BIS Billing 3.0 compliant XML
    peppol_xml = generate_peppol_xml(invoice_data)
    
    # Sign XML with company digital certificate
    signed_xml = sign_peppol_xml(peppol_xml, app_config['digital_certificate'])
    
    # Submit to Access Point Provider
    try:
        response = app_config['api_client'].submit_invoice(
            sender_id=invoice_data['supplier']['endpoint_id'],
            receiver_id=invoice_data['customer']['endpoint_id'],
            document_type='urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            document=signed_xml
        )
        
        if response['success']:
            # Store submission details
            submission_record = InvoiceSubmission.objects.create(
                invoice_number=invoice_data['header']['invoice_number'],
                company_uen=invoice_data['supplier']['uen'],
                customer_uen=invoice_data['customer']['uen'],
                submission_date=timezone.now(),
                transaction_id=response['transaction_id'],
                status='submitted',
                peppol_message_id=response['message_id']
            )
            
            return {
                'success': True,
                'transaction_id': response['transaction_id'],
                'message_id': response['message_id'],
                'submission_record_id': submission_record.id
            }
        else:
            raise InvoiceSubmissionError(f"Access Point Provider error: {response['error']}")
    
    except Exception as e:
        logger.error(f"InvoiceNow submission error: {str(e)}", exc_info=True)
        raise InvoiceSubmissionError(f"Failed to submit to InvoiceNow: {str(e)}")

def process_peppol_acknowledgment(message_id, status_code, status_description):
    """Process PEPPOL acknowledgment from Access Point Provider"""
    
    try:
        submission = InvoiceSubmission.objects.get(peppol_message_id=message_id)
        
        # Update submission status
        submission.status = 'acknowledged' if status_code == '200' else 'failed'
        submission.acknowledgment_date = timezone.now()
        submission.status_description = status_description
        submission.save()
        
        # Send notification to company
        if status_code == '200':
            send_success_notification(submission)
        else:
            send_failure_notification(submission, status_description)
        
        # Schedule reminder if not paid within due date
        if status_code == '200':
            schedule_payment_reminder(submission)
        
        return {
            'success': True,
            'submission_id': submission.id,
            'new_status': submission.status
        }
    
    except InvoiceSubmission.DoesNotExist:
        logger.warning(f"PEPPOL acknowledgment received for unknown message ID: {message_id}")
        return {
            'success': False,
            'error': 'Unknown message ID'
        }
```

### 7.2 PDPA Compliance

#### 7.2.1 Data Protection Framework
```python
class PDPAComplianceFramework:
    """Comprehensive PDPA compliance framework"""
    
    def __init__(self, company):
        self.company = company
        self.consent_purposes = [
            'order_processing',          # Essential for business operations
            'marketing_communications',  # Promotional emails/SMS
            'analytics_improvement',     # Service improvement and personalization
            'third_party_sharing',       # Sharing with partners (logistics, payment gateways)
            'legal_compliance',          # Regulatory and legal requirements
        ]
        self.data_retention_policies = {
            'transaction_data': 7 * 365,    # 7 years for financial records (ACRA/IRAS)
            'customer_data': 3 * 365,      # 3 years for customer data
            'marketing_data': 365,         # 1 year for marketing preferences
            'log_data': 90,                # 90 days for system logs
            'backup_data': 30,             # 30 days for backups
        }
    
    def obtain_consent(self, customer_id, purpose, method='explicit', context=None):
        """Record customer consent for data processing with audit trail"""
        
        if purpose not in self.consent_purposes:
            raise ValueError(f"Invalid consent purpose: {purpose}")
        
        # Get customer record
        customer = Customer.objects.get(id=customer_id)
        
        # Create consent record
        consent = DataConsent.objects.create(
            customer=customer,
            company=self.company,
            purpose=purpose,
            method=method,
            timestamp=timezone.now(),
            ip_address=context.get('ip_address') if context else None,
            user_agent=context.get('user_agent') if context else None,
            session_id=context.get('session_id') if context else None,
            consent_version='1.0'
        )
        
        # Update customer consent preferences
        customer_consent, created = CustomerConsent.objects.get_or_create(
            customer=customer,
            company=self.company,
            defaults={'consent_preferences': {}}
        )
        
        # Update consent preferences
        preferences = customer_consent.consent_preferences or {}
        preferences[purpose] = {
            'granted': True,
            'timestamp': timezone.now().isoformat(),
            'method': method,
            'version': '1.0'
        }
        customer_consent.consent_preferences = preferences
        customer_consent.save()
        
        # Log consent event
        self.log_consent_event(customer, purpose, 'granted', method)
        
        # Send confirmation if required
        if purpose == 'marketing_communications':
            self.send_consent_confirmation(customer, purpose)
        
        return consent
    
    def withdraw_consent(self, customer_id, purpose):
        """Process consent withdrawal with proper data handling"""
        
        customer = Customer.objects.get(id=customer_id)
        
        # Find existing consent
        try:
            consent = DataConsent.objects.filter(
                customer=customer,
                company=self.company,
                purpose=purpose,
                withdrawn_at__isnull=True
            ).latest('timestamp')
            
            # Mark consent as withdrawn
            consent.withdrawn_at = timezone.now()
            consent.save()
            
            # Update customer consent preferences
            customer_consent = CustomerConsent.objects.get(customer=customer, company=self.company)
            preferences = customer_consent.consent_preferences or {}
            
            if purpose in preferences:
                preferences[purpose]['granted'] = False
                preferences[purpose]['withdrawn_at'] = timezone.now().isoformat()
                customer_consent.consent_preferences = preferences
                customer_consent.save()
            
            # Handle data based on purpose
            self.handle_consent_withdrawal_data(customer, purpose)
            
            # Log withdrawal event
            self.log_consent_event(customer, purpose, 'withdrawn', 'customer_request')
            
            return consent
            
        except DataConsent.DoesNotExist:
            raise ConsentNotFoundError(f"No active consent found for purpose: {purpose}")
    
    def handle_consent_withdrawal_data(self, customer, purpose):
        """Handle data processing based on consent withdrawal"""
        
        if purpose == 'marketing_communications':
            # Stop marketing communications immediately
            self.stop_marketing_communications(customer)
            # Anonymize marketing preference data after 30 days
            schedule_anonymization(customer.id, 'marketing_data', days=30)
        
        elif purpose == 'analytics_improvement':
            # Remove personal identifiers from analytics data
            self.anonymize_analytics_data(customer)
            # Stop collecting analytics data for this customer
            self.stop_analytics_collection(customer)
        
        elif purpose == 'third_party_sharing':
            # Revoke data sharing permissions with third parties
            self.revoke_third_party_permissions(customer)
            # Request third parties to delete shared data
            self.request_third_party_deletion(customer)
        
        elif purpose == 'order_processing':
            # Critical business purpose - cannot fully withdraw
            # Instead, minimize data collection and provide notification
            self.minimize_order_processing_data(customer)
            self.send_data_minimization_notice(customer)
        
        # Log data handling actions
        self.log_data_handling_actions(customer, purpose, 'withdrawal')
    
    def handle_data_access_request(self, customer_id, request_type='access'):
        """Process customer data access request (30-day requirement)"""
        
        customer = Customer.objects.get(id=customer_id)
        
        # Create data request record
        data_request = DataRequest.objects.create(
            customer=customer,
            company=self.company,
            request_type=request_type,
            status='processing',
            requested_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30)
        )
        
        # Collect all customer data based on request type
        if request_type == 'access':
            customer_data = self.collect_all_customer_data(customer)
        elif request_type == 'correction':
            customer_data = self.collect_data_for_correction(customer)
        elif request_type == 'deletion':
            customer_data = self.collect_data_for_deletion(customer)
        else:
            raise ValueError(f"Invalid request type: {request_type}")
        
        # Generate data report
        report = self.generate_data_report(customer_data, request_type)
        
        # Store report securely
        report_url = self.store_secure_report(report, data_request)
        
        # Log the request
        DataAccessLog.objects.create(
            data_request=data_request,
            customer=customer,
            request_date=timezone.now(),
            response_date=timezone.now(),
            data_provided=report_url,
            request_type=request_type
        )
        
        # Update request status
        data_request.status = 'completed'
        data_request.completed_at = timezone.now()
        data_request.report_url = report_url
        data_request.save()
        
        # Notify customer
        self.notify_customer_of_request_completion(customer, data_request, report_url)
        
        return {
            'request_id': data_request.id,
            'report_url': report_url,
            'completion_date': timezone.now()
        }
    
    def implement_data_retention_policy(self):
        """Automated data retention and deletion"""
        
        # Process each data type according to retention policy
        for data_type, retention_days in self.data_retention_policies.items():
            cutoff_date = timezone.now() - timedelta(days=retention_days)
            
            if data_type == 'transaction_data':
                self.delete_old_transaction_data(cutoff_date)
            elif data_type == 'customer_data':
                self.delete_old_customer_data(cutoff_date)
            elif data_type == 'marketing_data':
                self.delete_old_marketing_data(cutoff_date)
            elif data_type == 'log_data':
                self.delete_old_log_data(cutoff_date)
            elif data_type == 'backup_data':
                self.delete_old_backup_data(cutoff_date)
        
        # Log retention policy execution
        self.log_retention_policy_execution()
        
        return {
            'execution_date': timezone.now(),
            'policies_applied': len(self.data_retention_policies),
            'data_deleted': self.get_deletion_summary()
        }
    
    def process_data_breach(self, incident):
        """72-hour breach notification requirement"""
        
        # Step 1: Contain the breach
        containment_result = self.contain_breach(incident)
        
        # Step 2: Assess the impact
        impact_assessment = self.assess_breach_impact(incident)
        
        # Step 3: Notify PDPC within 72 hours if required
        if self.requires_pdpc_notification(impact_assessment):
            notification_result = self.notify_pdpc(incident, impact_assessment)
        
        # Step 4: Notify affected individuals if high risk
        if self.requires_individual_notification(impact_assessment):
            individual_notifications = self.notify_affected_individuals(incident, impact_assessment)
        
        # Step 5: Document everything
        incident_report = self.create_incident_report(incident, impact_assessment, containment_result)
        
        # Step 6: Implement remediation measures
        remediation_plan = self.create_remediation_plan(incident, impact_assessment)
        
        return {
            'incident_id': incident.id,
            'containment_status': containment_result['status'],
            'impact_level': impact_assessment['severity_level'],
            'pdpc_notified': notification_result['success'] if 'notification_result' in locals() else False,
            'individuals_notified': len(individual_notifications) if 'individual_notifications' in locals() else 0,
            'report_id': incident_report.id,
            'remediation_plan_id': remediation_plan.id
        }
```

### 7.3 Industry-Specific Compliance

#### 7.3.1 License Management Framework
```python
industry_licenses = {
    'food_beverage': {
        'authority': 'Singapore Food Agency (SFA)',
        'licenses': {
            'food_shop_license': {
                'requirement': 'All food establishments preparing/serving food',
                'validity': '1 year (renewable)',
                'fee': 'S$195 - S$390 depending on size',
                'processing_time': '4-6 weeks',
                'renewal_deadline': '1 month before expiry',
                'integration': 'GoBusiness Licensing Portal API'
            },
            'food_stall_license': {
                'requirement': 'Hawker stalls and food courts',
                'validity': '1 year (renewable)',
                'fee': 'S$130 - S$260',
                'processing_time': '3-4 weeks'
            },
            'import_license': {
                'requirement': 'Importing food products',
                'validity': '6 months',
                'fee': 'S$50 per application',
                'processing_time': '2-3 weeks'
            }
        },
        'additional_requirements': {
            'halal_certification': {
                'authority': 'MUIS Halal Certification',
                'validity': '2 years',
                'fee': 'S$600 - S$2,000',
                'requirements': 'Halal management system, staff training'
            },
            'food_handler_training': {
                'requirement': 'At least 1 trained staff per shift',
                'validity': '5 years',
                'training_providers': ['WSG', 'SkillsFuture']
            }
        },
        'compliance_monitoring': {
            'inspection_frequency': '2-4 times per year',
            'required_records': [
                'Daily temperature logs',
                'Supplier documentation',
                'Staff health records',
                'Cleaning schedules'
            ],
            'penalties': {
                'minor_infractions': 'Advisory letters',
                'major_infractions': 'Composition fines (S$500 - S$5,000)',
                'serious_violations': 'License suspension/revocation'
            }
        }
    },
    'health_beauty': {
        'authority': 'Health Sciences Authority (HSA)',
        'requirements': {
            'product_registration': {
                'requirement': 'All therapeutic products and medical devices',
                'categories': ['Medicines', 'Medical devices', 'Traditional medicines'],
                'processing_time': '3-6 months',
                'fee': 'S$650 - S$5,000 depending on complexity'
            },
            'cosmetic_notification': {
                'requirement': 'All cosmetic products',
                'processing_time': 'No approval required, notification only',
                'fee': 'No fee',
                'deadline': 'Before product launch'
            },
            'import_license': {
                'requirement': 'Importing regulated health products',
                'validity': '1 year',
                'fee': 'S$100 per application'
            }
        },
        'compliance_framework': {
            'gmp_requirement': 'Good Manufacturing Practice certification for manufacturers',
            'adverse_event_reporting': 'Mandatory reporting of adverse events within 15 days',
            'product_labeling': 'Bilingual labeling (English + other official language)',
            'shelf_life_monitoring': 'Regular quality checks and expiry tracking'
        },
        'digital_integration': {
            'hsa_portal': 'Electronic Product Registration System (ePRS)',
            'automated_notifications': 'Product expiry and renewal alerts',
            'batch_recall_system': 'Automated customer notification for recalls'
        }
    },
    'alcohol': {
        'authority': 'Singapore Police Force (SPF)',
        'license_types': {
            'class_1a_license': {
                'requirement': 'Restaurants and food establishments',
                'validity': '1 year',
                'fee': 'S$780',
                'operating_hours': 'No sales 10:30 PM - 7:00 AM',
                'restrictions': 'No sales to persons under 18'
            },
            'class_1b_license': {
                'requirement': 'Taverns, pubs, discotheques',
                'validity': '1 year', 
                'fee': 'S$1,300',
                'operating_hours': 'No sales 10:30 PM - 7:00 AM (extended hours possible)',
                'restrictions': 'No sales to persons under 18'
            },
            'class_2a_license': {
                'requirement': 'Supermarkets, convenience stores',
                'validity': '1 year',
                'fee': 'S$520',
                'operating_hours': 'No sales 10:30 PM - 7:00 AM',
                'restrictions': 'No sales to persons under 18'
            }
        },
        'compliance_requirements': {
            'id_verification': 'Mandatory ID check for customers appearing under 25',
            'staff_training': 'Responsible alcohol service training required',
            'cctv_requirements': 'CCTV coverage of sales areas and entrances',
            'incident_reporting': 'Report alcohol-related incidents to police'
        },
        'automated_compliance': {
            'age_verification_integration': 'ID scanning at POS terminals',
            'sales_monitoring': 'Real-time sales volume tracking',
            'closing_time_alerts': 'Automatic system shutdown at 10:30 PM',
            'license_renewal_tracking': '90-day advance renewal reminders'
        }
    },
    'retail_general': {
        'authority': 'ACRA and SLA',
        'basic_requirements': {
            'business_registration': {
                'requirement

** the document is cut off here, so this is the end of this PRD **
