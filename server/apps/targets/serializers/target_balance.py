from collections import OrderedDict

from rest_framework import serializers

from ..models import TargetBalance
from ...pockets.models import Transaction
from ...pockets.serializers import TransactionCreateSerializer


class TargetBalanceRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetBalance
        fields = ('id', 'percent',)


class TargetBalanceSerializer(serializers.ModelSerializer):
    transactions = TransactionCreateSerializer()

    class Meta:
        model = TargetBalance
        fields = ('id', 'transactions', 'percent',)

    def validate(self, attrs: dict) -> dict:
        if 'transactions' in self.context:
            attrs['transactions'] = self.context['transactions']
        return attrs

    def create(self, validated_data):
        transaction_data = validated_data.pop('transactions')
        transaction_data['user'] = self.context['request'].user
        transaction = Transaction.objects.create(**transaction_data)
        balance = TargetBalance.objects.create(**validated_data)
        balance.transactions.add(transaction)

        return balance

    @property
    def data(self) -> OrderedDict:
        return TargetBalanceRetrieveSerializer(instance=self.instance).data
