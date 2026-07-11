from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

# ================= U_VIEW ===================
from app_royale.u_views import (
    main, contact, products
)
# --------------------------------------------
urlpatterns += [
    path('', main.main_page, name="main_page"),
    path('products/', main.products, name="products"),
    path('api/products', products.more_products, name="more_products"),
    path('contact/', contact.contact_us, name="contact"),
]
# ============================================