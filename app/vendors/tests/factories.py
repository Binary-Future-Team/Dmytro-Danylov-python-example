from factory import Sequence, SubFactory
import factory
from faker import Faker

from vendors.models import Vendor

fake = Faker()


class VendorFactory(factory.django.DjangoModelFactory):
    """Vendor model factory"""

    brand_name = factory.Sequence(lambda x: fake.company() + str(x))
    company_legal_name = factory.Sequence(lambda x: fake.company() + str(x))
    company_number = factory.Sequence(lambda x: str(fake.random_number(6)))
    address_line_1 = factory.Sequence(lambda x: fake.address())
    address_line_2 = factory.Sequence(lambda x: fake.address())
    city = factory.Sequence(lambda x: fake.city())
    postcode = factory.Sequence(lambda x: fake.zipcode())
    country = factory.Sequence(lambda x: fake.country())
    creation_date = fake.date_time_this_month()


    class Meta:
        model = Vendor
