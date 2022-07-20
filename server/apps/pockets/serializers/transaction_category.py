from rest_framework import serializers

from ..constants import TransactionCategoryErrors
from ..models import TransactionCategory


class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = ('id', 'name')

    def validate(self, attrs: dict) -> dict:
        user = self.context['request'].user
        name = attrs['name']
        excludes = {'id': self.instance.id} if self.instance else {}

        if TransactionCategory.objects.filter(
            user=user,
            name=name,
        ).exclude(
            **excludes,
        ).exists():
            raise serializers.ValidationError({'name': TransactionCategoryErrors.ALREADY_EXISTS})
        else:
            return attrs

    def create(self, validated_data: dict) -> TransactionCategory:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionCategoryTransactionSumSerializer(serializers.ModelSerializer):
    transactions_sum = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = TransactionCategory
        fields = ('id', 'name', 'transactions_sum')


class TransactionCategoryTransactionsSerializer(serializers.Serializer):
    name = serializers.CharField()
    transactions_sum = serializers.DecimalField(max_digits=10, decimal_places=2)
