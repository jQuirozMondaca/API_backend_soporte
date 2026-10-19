from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudViewSet, LoginView, LogoutView, GetCSRFToken

router = DefaultRouter()
router.register(r'solicitudes', SolicitudViewSet, basename='solicitud')

urlpatterns = [
    path('auth/csrf/', GetCSRFToken.as_view(), name='csrf_token'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]