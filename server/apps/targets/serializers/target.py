from django.utils import timezone
from rest_framework import serializers

from ..constants import TargetErrors
from ..models import Target
from ...pockets.models import Transaction


class TargetListSerializer(serializers.ModelSerializer):
    transactions_sum = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date', 'target_amount',
            'target_term', 'transactions_sum', 'percent',
            'initial_payment', 'category', 'is_open',
        )


class TargetRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date', 'target_amount',
            'target_term', 'is_open',
            'percent', 'initial_payment', 'category',
        )


class TargetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = (
            'id', 'name',
            'target_term', 'category',
            'balances', 'target_amount',
            'percent', 'initial_payment',
        )

    def validate(self, attrs: dict) -> dict:
        user = self.context['request'].user
        name = attrs.get('name', None)
        is_open = self.instance.is_open if self.instance else True
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
        init_pay = attrs.get('initial_payment', None)
        if init_pay and self.instance.initial_payment:
            raise serializers.ValidationError(TargetErrors.FIELD_NOT_EDITABLE)
        if not is_open:
            raise serializers.ValidationError(TargetErrors.TARGET_IS_CLOSED)

        return attrs

    def create(self, validated_data: dict) -> Target:
        validated_data['user'] = self.context['request'].user
        validated_data['create_date'] = timezone.now()
        return super().create(validated_data)
