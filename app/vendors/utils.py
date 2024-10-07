from typing import Optional
from django.http import HttpRequest

from vendors.models import VendorShopConnection


def get_connection_obj(
    request: Optional[HttpRequest] = None,
    connection_obj: Optional[VendorShopConnection] = None,
    connection_id: Optional[int] = None,
) -> VendorShopConnection:
    if request:
        connection_obj = request.user.shop_connection  # noqa

    if not connection_obj and connection_id:
        connection_obj = VendorShopConnection.objects.filter(pk=connection_id).first()

    if not connection_obj:
        raise Exception("Connection not defined")

    return connection_obj
