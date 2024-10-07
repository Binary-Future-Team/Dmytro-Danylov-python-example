from django.apps import apps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.urls import reverse

from core.admin import AdminSite
from vendors.models import VendorShopConnection
from vendors.tasks import import_shop_products
from vendors.utils import get_connection_obj


@login_required
@user_passes_test(lambda u: u.has_perm("vendors.view_vendorshopconnection"))
def integration(request):
    if request.user.is_superuser:
        return redirect("/admin/vendors/vendorshopconnection/")

    # redirect to the edit connection page if it is already setup
    connection_obj = request.user.shop_connection
    if not connection_obj:
        return redirect("/admin/vendors/vendorshopconnection/add/")

    admin_site = AdminSite()

    # Use each_context to get the admin context
    admin_context = admin_site.each_context(request)

    shop_url = connection_obj.shop_url
    change_connection_url = "/admin/vendors/vendorshopconnection/%s/change/" % connection_obj.pk
    disconnect_url = reverse("disconnect-store")

    installed_apps = [app_config.verbose_name for app_config in apps.get_app_configs()]

    # Combine the admin context with your custom data
    context = {
        **admin_context,
        "shop_url": shop_url,
        "disconnect_url": disconnect_url,
        "change_connection_url": change_connection_url,
        "title": "E-Commerce Integration",
        "available_apps": installed_apps,
        "import_product_link": "/import-products/",
    }

    return render(request, "admin/vendors/vendorshopconnection/integration-page.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class ShopifyUninstallAppView(View):
    def post(self, request, *args, **kwargs):
        connection_obj = VendorShopConnection.objects.filter(id=kwargs["pk"]).first()
        if connection_obj:
            from products.models import Product

            Product.objects.filter(vendor=connection_obj.vendor).update(
                status=Product.STATUS_SHOP_DISCONNECTED,
                status_updated=timezone.now(),
            )

            connection_obj.delete()

        return JsonResponse({"status": "Ok"})


@login_required
@user_passes_test(lambda u: u.has_perm("vendors.view_vendorshopconnection"))
def disconnect_store(request):
    from products.models import Product

    vendor = request.user.vendor
    url = reverse("admin:integration")
    if not vendor:
        return redirect(url)

    # Remove connection object
    connection_obj = VendorShopConnection.objects.filter(vendor=vendor).first()
    if connection_obj:
        connection_obj.delete()

    # Remove vendor relation from all product that was connected to this vendor
    Product.objects.filter(vendor=vendor).update(
        status=Product.STATUS_SHOP_DISCONNECTED,
        status_updated=timezone.now(),
    )

    return redirect(url)


@login_required
@user_passes_test(lambda u: u.has_perm("vendors.view_vendorshopconnection"))
def import_products(request):
    import_shop_products.delay(get_connection_obj(request=request).pk, is_manual_import=True)
    return redirect("/admin/products/product/")
