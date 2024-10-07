from django.urls import path

from . import views

urlpatterns = [
    path("import-products/", views.import_products, name="import-products"),
    path("disconnect-store/", views.disconnect_store, name="disconnect-store"),
    path(
        "webhook/shopify/<int:pk>/uninstall/",
        views.ShopifyUninstallAppView.as_view(),
        name="uninstall_shopify_app",
    ),
]
