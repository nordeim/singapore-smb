"""
Factory classes for accounts tests.

Uses factory_boy to create test data for:
- Company
- User
- Role
- UserRole
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.hashers import make_password

from apps.accounts.models import Company, User, Role, UserRole


class CompanyFactory(DjangoModelFactory):
    """Factory for creating Company instances."""
    
    class Meta:
        model = Company
    
    name = factory.Faker('company')
    legal_name = factory.LazyAttribute(lambda obj: f"{obj.name} Pte Ltd")
    uen = factory.Sequence(lambda n: f'2024{n:05d}A')
    email = factory.Faker('company_email')
    phone = factory.Sequence(lambda n: f'+65{80000000 + (n % 9999999):07d}')
    address_line1 = factory.Faker('street_address')
    postal_code = factory.Sequence(lambda n: f'{100000 + n:06d}'[:6])
    plan_tier = 'standard'
    gst_registered = False


class GSTRegisteredCompanyFactory(CompanyFactory):
    """Factory for creating GST-registered companies."""
    
    gst_registered = True
    gst_registration_number = factory.Sequence(lambda n: f'M{n:08d}')
    gst_registration_date = factory.Faker('date_this_decade')


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Sequence(lambda n: f'+65{90000000 + (n % 9999999):07d}')
    company = factory.SubFactory(CompanyFactory)
    is_active = True
    is_verified = True
    password = factory.LazyFunction(lambda: make_password('testpass123'))
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to handle password properly."""
        password = kwargs.pop('password', None)
        user = super()._create(model_class, *args, **kwargs)
        if password and not password.startswith('pbkdf2_'):
            user.set_password(password)
            user.save()
        return user


class SuperUserFactory(UserFactory):
    """Factory for creating superusers."""
    
    is_superuser = True
    company = None


class RoleFactory(DjangoModelFactory):
    """Factory for creating Role instances."""
    
    class Meta:
        model = Role
    
    name = factory.Sequence(lambda n: f'role_{n}')
    description = factory.Faker('sentence')
    company = factory.SubFactory(CompanyFactory)
    permissions = factory.LazyFunction(lambda: ['users.view', 'orders.view'])
    is_system = False


class OwnerRoleFactory(RoleFactory):
    """Factory for creating owner roles."""
    
    name = 'owner'
    description = 'Company owner with full access'
    permissions = factory.LazyFunction(lambda: ['all'])


class AdminRoleFactory(RoleFactory):
    """Factory for creating admin roles."""
    
    name = 'admin'
    description = 'Administrative access'
    permissions = factory.LazyFunction(lambda: [
        'users.view', 'users.create', 'users.update', 'users.delete',
        'products.view', 'products.create', 'products.update', 'products.delete',
        'orders.view', 'orders.update',
    ])


class UserRoleFactory(DjangoModelFactory):
    """Factory for creating UserRole instances."""
    
    class Meta:
        model = UserRole
    
    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)
    assigned_by = None
