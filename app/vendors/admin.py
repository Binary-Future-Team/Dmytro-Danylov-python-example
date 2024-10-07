from uuid import uuid4

from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from categories.models.categories import SubCategory
from core.admin import admin as base_admin
from vendors import forms, models
from vendors.models import VendorShopConnection
from vendors.views import integration


class SuperuserAdmin(ModelAdmin):

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        context["show_save_and_add_another"] = False
        context["show_save_and_continue"] = False
        return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)


class VendorCommissionInline(TabularInline):
    """Inline admin class to render vendor commissions"""

    model = models.VendorCommission
    extra = 0
    form = forms.VendorCommissionForm
    template = "admin/vendors/commissions/tabular.html"


class VendorAdmin(SuperuserAdmin):
    """Admin class to render vendor entry"""

    list_display_links = (
        "brand_name",
        "company_legal_name",
    )
    list_display = ("brand_name", "company_legal_name", "city", "country", "user")
    list_filter = (
        "brand_name",
        "company_legal_name",
    )
    search_fields = (
        "brand_name",
        "company_legal_name",
        "company_number",
        "city",
        "country",
    )
    ordering = ("creation_date",)
    list_per_page = 20
    form = forms.VendorAdminForm
    readonly_fields = ("creation_date",)
    inlines = [VendorCommissionInline]

    fieldsets = (
        (
            "Vendor Company Info",
            {
                "fields": (
                    "brand_name",
                    "company_legal_name",
                    "vat_number",
                    "address_line_1",
                    "company_number",
                    "address_line_2",
                    "city",
                    "postcode",
                    "country",
                    "logo",
                    "is_send_receipt",
                    "is_payment_pending",
                ),
                "classes": ("vendor-company-info",),
            },
        ),
        (
            "Vendor Administrator",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "creation_date",
                ),
                "classes": ("vendor-administrator",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        User = get_user_model()
        try:
            obj.user
        except User.DoesNotExist:
            user = User()
            user.vendor = obj
            obj.user.username = uuid4().hex
            obj.user.is_staff = True

        obj.user.email = form.cleaned_data["email"]
        obj.user.first_name = form.cleaned_data["first_name"]
        obj.user.last_name = form.cleaned_data["last_name"]
        obj.user.phone = form.cleaned_data["phone"]
        obj.user.save(create_confirm=True)
        vendor_group = Group.objects.filter(name=User.VENDOR_GROUP_NAME).first()
        vendor_group.user_set.add(obj.user)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        user = obj.user
        super().delete_model(request, obj)
        user.delete()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:  # just using request.user attributes
            queryset = queryset.filter(id=request.user.vendor.id)
        return queryset

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("user-settings/", self.usersettings_view, name="user-settings"),
            path("<int:object_id>/delete-commission/", self.deletecommission_view, name="deletecommission"),
        ]
        return custom_urls + urls

    def usersettings_view(self, request):
        """Custom admin view to render vendor settings only. Superuser will be redirected to vendors list page."""
        if not request.user.is_authenticated:
            return redirect("/login/")
        if request.user.is_superuser:
            url = reverse("admin:vendors_vendor_changelist")
            return redirect(url)
        vendor = request.user.vendor
        context = self.admin_site.each_context(request)
        context["vendor"] = vendor
        context["subcategories"] = SubCategory.objects.filter(
            id__in=vendor.products.values_list("sub_category_id", flat=True)
        ).exclude(id__in=vendor.commissions.values_list("subcategory_id", flat=True))
        return TemplateResponse(request, "admin/vendors/settings/user-settings.html", context)

    def deletecommission_view(self, request, object_id):
        """Custom admin view to render vendor settings only. Superuser will be redirected to vendors list page."""
        if not request.user.is_authenticated:
            return redirect("/login/")
        if not request.user.is_superuser:
            url = reverse("admin:orders_order_changelist")
            return redirect(url)
        entry = models.VendorCommission.objects.get(id=object_id)
        if not entry:
            messages.error(request, "Vendor commission is already deleted.")
            url = reverse("admin:vendors_vendor_changelist")
            return redirect(url)
        if request.META["REQUEST_METHOD"] != "DELETE":
            messages.error(request, "Wrong HTTP method.")
            url = reverse("admin:vendors_vendor_changelist")
            return redirect(url)
        # generate url to vendor change list
        url = reverse("admin:vendors_vendor_change", kwargs={"object_id": entry.vendor.pk})
        entry.delete()
        messages.error(request, "Vendor commission was deleted successfully.")
        return redirect(url)


class VendorShopConnectionAdmin(SuperuserAdmin):
    list_display = (
        "vendor",
        "shop_url",
    )
    form = forms.VendorShopConnectionAdminForm

    fieldsets = (
        (
            "Connection Info",
            {
                "fields": (
                    "shop_url",
                    "access_token",
                    "api_key",
                    "api_secret_key",
                ),
                "classes": (),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("integration/", integration, name="integration"),
        ]
        return custom_urls + urls

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:  # just using request.user attributes
            queryset = queryset.filter(vendor=request.user.vendor)
        return queryset

    def save_model(self, request, obj: VendorShopConnection, form, change):
        connections = VendorShopConnection.objects.filter(vendor=request.user.vendor)
        if obj.id:
            connections = connections.exclude(id=obj.id)
        connections.delete()
        obj.vendor = request.user.vendor
        obj.is_shop_valid = True
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if not request.user.is_superuser:
            return redirect("/admin/vendors/vendorshopconnection/integration/")

        return super().changelist_view(request, extra_context=extra_context)


base_admin.register(models.Vendor, VendorAdmin)
base_admin.register(models.VendorShopConnection, VendorShopConnectionAdmin)
