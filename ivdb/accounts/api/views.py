from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from accounts.models import Profile
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': profile.bio if profile else "",
            'is_staff': user.is_staff,
        })
    
    def patch(self, request):
        user = request.user
        data = request.data
        
        # Actualizar email
        if 'email' in data:
            user.email = data['email']
        
        # Actualizar contraseña
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Actualizar bio (en el perfil)
        if 'bio' in data:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.bio = data['bio']
            profile.save()
        
        user.save()
        
        return Response({
            'message': 'Perfil actualizado correctamente',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': getattr(user, 'profile', None).bio if hasattr(user, 'profile') else "",
            }
        })
    
    def delete(self, request):
        user = request.user
        username = user.username
        user.delete()
        return Response(
            {'message': f'Usuario {username} eliminado correctamente'},
            status=status.HTTP_200_OK
        )
