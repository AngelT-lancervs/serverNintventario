from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email', 'password']

class ProductSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    stock_inicial = serializers.IntegerField()
    stock_final = serializers.IntegerField()
