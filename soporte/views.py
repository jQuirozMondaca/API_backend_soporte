from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Solicitud
from .serializers import SolicitudSerializer
from .permissions import IsOwnerOrAdmin

# Obtención del token CSRF necesario para POST/PUT/DELETE bajo SessionAuthentication
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"detail": "CSRF cookie establecida."}, status=status.HTTP_200_OK)

# Inicio de sesión
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "detail": "Inicio de sesión exitoso.",
                "user": user.username,
                "is_staff": user.is_staff
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

# Cierre de sesión
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)

# ViewSet de Solicitudes
class SolicitudViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Solicitud.objects.all().order_by('-fecha_creacion')
        return Solicitud.objects.filter(usuario=user).order_by('-fecha_creacion')

    def perform_create(self, serializer):
        # Asignación automática del usuario autenticado en el servidor
        serializer.save(usuario=self.request.user)