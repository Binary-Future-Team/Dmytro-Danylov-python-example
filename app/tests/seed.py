import random
from brands.tests.factories import BrandFactory
from categories.tests.factories import CategoryFactory, SubCategoryFactory
from orders.tests.factories import OrderFactory, AgreementFactory
from products.tests.factories import ProductFactory, VariantFactory
from vendors.tests.factories import VendorFactory
from users.tests.factories import UserFactory
# vendor is also have been created

from faker import Faker

from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.filter(email='qqq@aaa.aa').first()
vendor = user.vendor


#vendor = VendorFactory.create()
#user = UserFactory.create(vendor=vendor)
brand = BrandFactory.create()
category = CategoryFactory.create()
sub_categories = []
for x in range(random.randint(0, 10)):
    sub_category = SubCategoryFactory.create(parent=category)
    sub_categories.append(sub_category)
for x in range(200 + random.randint(-50, 50)):
    product = ProductFactory.create(vendor=vendor, brand=brand, category=category, sub_category=random.choice(sub_categories))
    print (product.product_id)
    for y in range(random.randint(0, 3)):
        variant = VariantFactory.create(product=product)

for x in range(200 + random.randint(-50, 50)):
    order = OrderFactory.create()
    agreement = AgreementFactory.create(order=order, variant=variant)
