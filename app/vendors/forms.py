from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField

from categories.models.categories import SubCategory
from core.validators import ImageMaxSizeValidator
from vendors import models


class VendorCommissionForm(forms.ModelForm):
    subcategory = forms.ModelChoiceField(label="Nested Category", queryset=SubCategory.objects.all())
    commission = forms.FloatField(label="Commission (%)", required=False)

    class Meta:
        model = models.VendorCommission
        fields = [
            "subcategory",
            "commission",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for x in SubCategory.objects.all():
            choices.append([x.pk, f"{x.parent.name} | {x.name} ({x.commission} %)"])
        self.fields["subcategory"].choices = choices


class VendorAdminForm(forms.ModelForm):
    # company
    brand_name = forms.CharField()
    company_legal_name = forms.CharField()
    company_number = forms.CharField()
    address_line_1 = forms.CharField(required=False)
    address_line_2 = forms.CharField(required=False)
    city = forms.CharField(required=False)
    postcode = forms.CharField(required=False)
    country = forms.CharField(required=False)

    # vendor admin
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = PhoneNumberField()

    class Meta:
        model = models.Vendor
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            user = instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email.lower()
            self.fields["phone"].initial = user.phone

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        User = get_user_model()
        if not self.instance.pk:
            # if user is new, don`t let it create existing email
            if User.objects.filter(email=email).exists():
                raise ValidationError("Email already exists")
        else:
            # if user is old
            # check if email has changed and don`t let it create existing email
            if self.instance.user.email != email and User.objects.filter(email=email).exists():
                raise ValidationError("Email already exists")
        return email

    def clean_company_number(self):
        value = self.cleaned_data["company_number"]
        try:
            company_number = int(value)
        except ValueError:
            raise ValidationError("Company number is not numeric!")
        if company_number <= 0:
            raise ValidationError("Company number is less than 0!")
        return value


class VendorShopConnectionAdminForm(forms.ModelForm):
    model = models.VendorShopConnection

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["shop_url"].widget.attrs.update(
            {
                "placeholder": "https://***.myshopify.com"
            }
        )
        # Check if the form instance has a primary key
        if self.instance and self.instance.pk:
            # Disable a field when editing
            self.fields["shop_url"].disabled = True


class UserSettingsForm(forms.ModelForm):
    bike_commission = forms.FloatField(label="Bike Commission (%)", disabled=True, required=False)
    accessories_commission = forms.FloatField(label="Accessories Commission (%)", disabled=True, required=False)
    clothing_commission = forms.FloatField(label="Clothing Commission (%)", disabled=True, required=False)
    maintenance = forms.FloatField(label="Maintenance (%)", disabled=True, required=False)
    bike_parts = forms.FloatField(label="Bike Parts (%)", disabled=True, required=False)
    pre_owned = forms.FloatField(label="Pre-owned (%)", disabled=True, required=False)

    class Meta:
        model = models.Vendor
        fields = [
            "bike_commission",
            "accessories_commission",
            "clothing_commission",
            "maintenance",
            "bike_parts",
            "pre_owned",
        ]
