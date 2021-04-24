from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from server import views

import notifications.urls

urlpatterns = [
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('performers/', include('performer.urls')),
    path('customers/', include('customer.urls')),
    path('authentication/', include('authentication.urls')),
    path('orders/', include(('order.urls', 'order_app'))),
    path('admin/', admin.site.urls),
    path('profile/', include('user_profile.urls')),
    path('chat/', include('chat.urls')),
    path('', views.index, name="index"),
    path('notifications', views.notifications_handler, name="notifications_handler"),
    path('social-auth/', include('social_django.urls', namespace="social")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
