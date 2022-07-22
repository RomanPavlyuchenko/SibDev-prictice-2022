from django.utils import timezone
from rest_framework import serializers

from .target_balance import TargetBalanceRetrieveSerializer
from ..constants import TargetErrors
from ..models import Target


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date',
            'expected_amount', 'target_deadline',
        )


class TargetRetrieveSerializer(serializers.ModelSerializer):
    balance = TargetBalanceRetrieveSerializer()
    transactions_sum = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date', 'expected_amount',
            'target_deadline', 'balance', 'transactions_sum',
        )


class TargetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = (
            'id', 'name',
            'target_deadline', 'category',
            'balance', 'expected_amount',
        )

    def is_valid(self, raise_exception=False):
        return super().is_valid(raise_exception)

    def validate(self, attrs: dict) -> dict:
        user = self.context['request'].user
        name = attrs.get('name', None)
        excludes = {'id': self.instance.id} if self.instance else {}

        if name and Target.objects.filter(
            user=user,
            name=name,
        ).exclude(
            **excludes,
        ).exists():
            raise serializers.ValidationError(TargetErrors.ALREADY_EXISTS)
        category = attrs.get('category', None)
        if category and category not in user.categories.all():
            raise serializers.ValidationError(TargetErrors.NOT_USERS_CATEGORY)

        return attrs

    def create(self, validated_data: dict) -> Target:
        validated_data['user'] = self.context['request'].user
        validated_data['create_date'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('expected_amount') < instance.expected_amount:
            raise serializers.ValidationError(TargetErrors.EXPECTED_AMOUNT_TOO_LOW)
        return super().update(instance, validated_data)
