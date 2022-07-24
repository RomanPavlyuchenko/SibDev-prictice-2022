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
            'initial_payment', 'category',
        )


class TargetRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date', 'target_amount',
            'target_term', 'transactions_sum',
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
        editable_fields = ('name', 'target_term', 'percent', 'target_amount')
        forbidden_fields = set(self.Meta.fields).difference(editable_fields).intersection(attrs)
        user = self.context['request'].user
        name = attrs.get('name', None)
        user_balance = Transaction.objects.get_queryset().filter(
            user=user
        ).aggregate_balance()['balance']
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
        if init_pay and init_pay > user_balance:
            raise serializers.ValidationError(TargetErrors.BALANCE_TOO_LOW)
        if excludes and forbidden_fields:
            raise serializers.ValidationError({
                attr: TargetErrors.FIELD_NOT_EDITABLE for attr in forbidden_fields
            })

        return attrs

    def create(self, validated_data: dict) -> Target:
        validated_data['user'] = self.context['request'].user
        validated_data['create_date'] = timezone.now()
        return super().create(validated_data)
