from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Company, User
from apps.accounts.services import CompanyService


class Command(BaseCommand):
    help = 'Seed minimal Phase 1 data (company, default roles, owner user).'

    def add_arguments(self, parser):
        parser.add_argument('--uen', default='201812345A')
        parser.add_argument('--company-name', default='Singapore SMB Demo')
        parser.add_argument('--company-email', default='contact@demo.local')
        parser.add_argument('--owner-email', default='owner@demo.local')
        parser.add_argument('--owner-password', default='ChangeMe123!')

    @transaction.atomic
    def handle(self, *args, **options):
        uen = str(options['uen']).upper()

        company = Company.objects.filter(uen=uen).first()
        if company is None:
            company, owner = CompanyService.create_company(
                name=options['company_name'],
                uen=uen,
                email=options['company_email'],
                owner_email=options['owner_email'],
                owner_password=options['owner_password'],
            )
            self.stdout.write(self.style.SUCCESS(f'Created company {company.uen} and owner {owner.email}'))
            return

        CompanyService.create_default_roles(company)

        owner = User.objects.filter(email=str(options['owner_email']).lower()).first()
        if owner is None:
            owner = User.objects.create_user(
                email=str(options['owner_email']).lower(),
                password=options['owner_password'],
                company=company,
                is_verified=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Created owner user {owner.email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Owner user already exists: {owner.email}'))

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
