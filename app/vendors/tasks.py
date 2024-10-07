from datetime import timedelta
from typing import Optional

from celery.utils.log import get_task_logger
from django.db.models import Prefetch, Count
from django.utils import timezone

from core import celery_app as app
from core.klaviyo import Klaviyo
from core.shopify.rest_client import ShopifyClient
from pyactiveresource.connection import ClientError

from products.models import Product

from vendors.models import VendorShopConnection, Vendor
from vendors.utils import get_connection_obj

logger = get_task_logger(__name__)


@app.task(bind=True)
def sync_vendors_products(self):
    connections = VendorShopConnection.objects.filter(is_shop_valid=True)
    for connection in connections:
        import_shop_products.delay(connection.pk)


@app.task(bind=True)
def import_shop_products(self, connection_id: Optional[int] = None, is_manual_import: bool = False):
    from products.models import Product, ProductImage, Variant
    from products.services import ProductService

    connection_obj = get_connection_obj(connection_id=connection_id)
    client = ShopifyClient(connection_obj=connection_obj)
    try:
        service = ProductService(connection_obj)
    except ClientError as error:
        logger.error(f"Shopify connection error: {error}")
        if not 401 <= error.response.code <= 404:
            raise
        connection_obj.is_shop_valid = False
        connection_obj.save(update_fields=["is_shop_valid", "updated_at"])
        return

    products_extra_data = client.get_products_extra_data()
    updated_products = []

    for products_chunk in client.get_products():
        for product in products_chunk:
            try:
                service.create_or_update_product(
                    product,
                    products_extra_data.exclude_variants,
                    products_extra_data.products_categories,
                    allow_create=is_manual_import,
                )
                updated_products.append(product.attributes["id"])
            except Exception as error:
                logger.error(f"Error while importing product {product.attributes['id']}: {error}")

    Product.objects.filter(vendor=connection_obj.vendor).exclude(product_id__in=updated_products).update(
        status=Product.STATUS_DELETED
    )
    ProductImage.objects.filter(
        product__vendor=connection_obj.vendor,
        product__status=Product.STATUS_DELETED,
    ).delete()

    Variant.objects.filter(
        product__vendor=connection_obj.vendor,
        product__status=Product.STATUS_DELETED,
    ).update(deleted=True)


@app.task
def clear_archived_products():
    Product.objects.filter(
        status__in=[Product.STATUS_ARCHIVED, Product.STATUS_SHOP_DISCONNECTED],
        status_updated__lt=timezone.now() - timedelta(days=14),
    ).update(
        vendor=None,
        status=Product.STATUS_DELETED,
    )


@app.task
def notify_vendor_about_unsynced_products():
    vendors = (
        Vendor.objects.prefetch_related(
            Prefetch("products", queryset=Product.objects.filter(status=Product.STATUS_UNSYNCED))
        )
        .annotate(products_count=Count("products"))
        .filter(products_count__gt=0)
    )
    for vendor in vendors:
        try:
            logger.info(f"Sending email about unsynced products to {vendor}")
            Klaviyo().send_vendor_unsynced_products_email(vendor, vendor.products.all())
        except Exception as error:
            logger.error(f"Failed to send email about unsynced products to {vendor.brand_name}. Error: {error}")
