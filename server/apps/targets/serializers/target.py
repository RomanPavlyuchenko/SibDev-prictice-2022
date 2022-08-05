from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from ..constants import TargetErrors
from ..models import Target
from ...pockets.models import Transaction, TransactionCategory
from ...pockets.serializers import TransactionCategorySerializer


class TargetListSerializer(serializers.ModelSerializer):
    transactions_sum = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date', 'target_amount',
            'target_term', 'transactions_sum', 'percent',
            'initial_payment', 'category', 'is_closed',
            'closing_date',
        )


class TargetRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Target
        fields = (
            'id', 'name', 'create_date', 'target_amount',
            'target_term', 'percent', 'initial_payment', 'category',
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
        editable_fields = (
            'name', 'target_term', 'percent', 'target_amount',
        )

    def validate(self, attrs: dict) -> dict:
        user = self.context['request'].user
        name = attrs.get('name', None)
        new_term = attrs.get('target_term', None)
        excludes = {'id': self.instance.id} if self.instance else {}

        if name and Target.objects.filter(
            user=user,
            name=name,
        ).exclude(
            **excludes,
        ).exists():
            raise serializers.ValidationError(TargetErrors.ALREADY_EXISTS)

        if self.instance and new_term:
            been_months = (datetime.now().date() - self.instance.create_date).days // 30
            if new_term < self.instance.target_term - been_months:
                raise serializers.ValidationError(TargetErrors.TARGET_TERM_TOO_LOW)

        return attrs

    def validate_category(self, category):
        user = self.context['request'].user
        if category not in user.categories.all():
            raise serializers.ValidationError(TargetErrors.NOT_USERS_CATEGORY)
        return category

    def validate_initial_payment(self, initial_payment):
        user = self.context['request'].user
        user_balance = Transaction.objects.get_queryset().filter(
            user=user
        ).aggregate_balance()['balance']
        if initial_payment > user_balance:
            raise serializers.ValidationError(TargetErrors.BALANCE_TOO_LOW)
        return initial_payment

    def create(self, validated_data: dict) -> Target:
        validated_data['user'] = self.context['request'].user
        validated_data['create_date'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'target_term' in validated_data:
            instance.create_date = timezone.now()
            instance.target_term = validated_data.pop('target_term')

        for attr, value in validated_data:
            if attr in self.Meta.editable_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class TargetAnalyticsSerializer(serializers.Serializer):
    open_targets_count = serializers.IntegerField()
    open_targets_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    percents_sum = serializers.DecimalField(max_digits=10, decimal_places=2)
    percents_sum_current_month = serializers.DecimalField(max_digits=10, decimal_places=2)
    fastest_finish = serializers.IntegerField()
    category_top = serializers.IntegerField(required=False)
    category_closed_top = serializers.IntegerField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        queryset = TransactionCategory.objects.all()

        data.update(
            {
                'category_top': TransactionCategorySerializer(
                    queryset.get(pk=instance['category_top'])
                ).data if instance['category_top'] else None,
                'category_closed_top': TransactionCategorySerializer(
                    queryset.get(pk=instance['category_closed_top'])
                ).data if instance['category_closed_top'] else None,
            }
        )
        return data
