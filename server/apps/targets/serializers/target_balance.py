from collections import OrderedDict

from rest_framework import serializers

from ..constants import TargetBalanceErrors
from ..models import TargetBalance
from ...pockets.models import Transaction
from ...pockets.serializers import TransactionCreateSerializer


class TargetBalanceRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetBalance
        fields = ('id', 'amount', 'transaction_date', 'target')


class TargetBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetBalance
        fields = ('id', 'amount', 'transaction_date', 'target')

    def create(self, validated_data):
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        user_balance = Transaction.objects.get_queryset().filter(
            user=user
        ).aggregate_balance()['balance']
        amount = attrs.get('amount', None)
        if amount and amount > user_balance:
            raise serializers.ValidationError(TargetBalanceErrors.BALANCE_TOO_LOW)
        return attrs

    @property
    def data(self) -> OrderedDict:
        return TargetBalanceRetrieveSerializer(instance=self.instance).data
