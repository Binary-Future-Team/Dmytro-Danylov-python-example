from django.core.exceptions import ValidationError
from django.db import models

from categories.models.categories import SubCategory
from core.validators import ImageMaxSizeValidator


class Vendor(models.Model):
    brand_name = models.CharField(max_length=200, verbose_name="Brand Name", blank=False)
    company_legal_name = models.CharField(max_length=200, verbose_name="Company Legal Name", blank=False)
    company_number = models.CharField(max_length=200, verbose_name="Company Number", blank=False)
    address_line_1 = models.CharField(max_length=200, verbose_name="Address Line 1", blank=True)
    address_line_2 = models.CharField(max_length=200, verbose_name="Address Line 2", blank=True)
    city = models.CharField(max_length=100, verbose_name="City", blank=True)
    postcode = models.CharField(max_length=50, verbose_name="Postcode", blank=True)
    country = models.CharField(max_length=100, verbose_name="Country", blank=True)
    creation_date = models.DateTimeField(verbose_name="Creation Time (UTC)", auto_now=True, blank=True)

    vat_number = models.CharField(max_length=255, verbose_name="VAT Number", default="", blank=True)
    is_send_receipt = models.BooleanField(default=True, verbose_name="Send Receipt", blank=False)
    is_payment_pending = models.BooleanField(default=False, verbose_name="Payment Pending", blank=False)

    logo = models.ImageField(
        upload_to="vendor/%Y/%m/%d/",
        validators=[ImageMaxSizeValidator(268, 268)],
        blank=True,
    )

    def __str__(self):
        return f"{self.brand_name}: {self.company_legal_name}"


class VendorCommission(models.Model):
    vendor = models.ForeignKey(Vendor, verbose_name="Vendor", on_delete=models.CASCADE, related_name="commissions")
    subcategory = models.ForeignKey(
        SubCategory, verbose_name="Nested Category", on_delete=models.CASCADE, related_name="commissions"
    )
    commission = models.FloatField(verbose_name="Commission (%)", blank=True, null=True)

    class Meta:
        unique_together = ["vendor", "subcategory"]

    def __str__(self):
        return f"{self.subcategory.name} commission"

    @property
    def adjusted_commission(self) -> float:
        return self.commission or self.subcategory.commission

    @property
    def commission_name(self) -> str:
        return " | ".join((self.subcategory.parent.name, self.subcategory.name))


class VendorShopConnection(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="shop_connection")
    shop_url = models.CharField(max_length=200, verbose_name="Your shop URL", unique=True)
    access_token = models.CharField(max_length=100, verbose_name="API Access Token")
    # unused for now
    api_key = models.CharField(max_length=100, verbose_name="API Key", null=True)
    # unused for now
    api_secret_key = models.CharField(max_length=100, verbose_name="API Secret Key", null=True)

    is_shop_valid = models.BooleanField(default=True, verbose_name="Is shop valid")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.vendor}: {self.shop_url}"

    def clean(self):
        from core.shopify.rest_client import ShopifyClient

        is_successful, message = ShopifyClient(connection_obj=self).check_connection(dry_run=True)
        if not is_successful:
            raise ValidationError(message)

    def save(self, *args, **kwargs):
        super(VendorShopConnection, self).save(*args, **kwargs)
        if self.is_shop_valid:
            self.refresh_webhooks()
            # self.add_metafields()

    def add_metafields(self):
        from core.shopify.rest_client import ShopifyClient

        client = ShopifyClient(connection_obj=self)
        client.add_metafields()

    def refresh_webhooks(self):
        from core.shopify.rest_client import ShopifyClient

        client = ShopifyClient(connection_obj=self)
        client.unregister_webhooks()
        client.register_webhooks()

    def delete(self, using=None, keep_parents=False):
        from core.shopify.rest_client import ShopifyClient

        if self.is_shop_valid:
            client = ShopifyClient(connection_obj=self)
            client.disconnect()

        return super().delete(using=using, keep_parents=keep_parents)
