from collections import OrderedDict

from rest_framework import serializers

from ..constants import TransactionErrors
from ..models import Transaction
from .transaction_category import TransactionCategorySerializer


class TransactionRetrieveSerializer(serializers.ModelSerializer):
    category = TransactionCategorySerializer()

    class Meta:
        model = Transaction
        fields = ('id', 'category', 'transaction_type', 'transaction_date', 'amount')


class TransactionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'category', 'transaction_date', 'amount')

    def validate(self, attrs: dict) -> dict:
        user = self.context['request'].user

        if attrs['transaction_type'] == 'income' and attrs['category'] is not None:
            raise serializers.ValidationError(TransactionErrors.INCOME_TRANSACTION_TYPE)
        if not attrs.get('category', None):
            raise serializers.ValidationError(TransactionErrors.FIELD_IS_REQUIRED)
        if attrs['category'] not in user.categories.all():
            raise serializers.ValidationError(TransactionErrors.NOT_USERS_CATEGORY)

        return attrs

    def create(self, validated_data: dict) -> Transaction:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    @property
    def data(self) -> OrderedDict:
        """
        Сделано для того, чтобы при создании объекта можно было передвавть id категории, а после
        создания поле категории возвращалось как объект
        """
        return TransactionRetrieveSerializer(instance=self.instance).data


class TransactionGlobalSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)


class TransactionBalanceSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
