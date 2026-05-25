from __future__ import annotations

from rest_framework import serializers

from apps.institutions.models import Institution, InstitutionSettings


class InstitutionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'short_name', 'code', 'institution_type', 'city', 'state', 'is_active', 'created_at']


class InstitutionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstitutionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']


class InstitutionSettingsSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = InstitutionSettings
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'institution']
