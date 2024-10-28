from rest_framework import serializers
from .models import Inventory, Pemilik

class PemilikSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pemilik
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    pemilik = PemilikSerializer(many=True)

    class Meta:
        model = Inventory
        fields = '__all__'
