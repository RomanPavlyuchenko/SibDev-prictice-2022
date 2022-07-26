from collections import OrderedDict

from rest_framework import serializers

from ..constants import TargetErrors
from ..models import TargetBalance
from ...pockets.models import Transaction
from ...pockets.serializers import TransactionCreateSerializer


class TargetBalanceRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetBalance
        fields = ('id', 'amount', 'transaction_date', 'target')


class TargetBalanceCreateSerializer(serializers.ModelSerializer):
    transaction = TransactionCreateSerializer()

    class Meta:
        model = TargetBalance
        fields = (
            'id', 'amount', 'transaction_date',
            'target', 'transaction',
        )

    def create(self, validated_data):
        Transaction.objects.create(
            **{**validated_data.pop('transaction')},
            user=self.context['request'].user
        )
        return super().create(validated_data)

    def validate_amount(self, amount):
        user = self.context['request'].user
        user_balance = Transaction.objects.get_queryset().filter(
            user=user
        ).aggregate_balance()['balance']
        if amount > user_balance:
            raise serializers.ValidationError(TargetErrors.BALANCE_TOO_LOW)
        return amount

    @property
    def data(self) -> OrderedDict:
        return TargetBalanceRetrieveSerializer(instance=self.instance).data
