from collections import OrderedDict

from rest_framework import serializers

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

    @property
    def data(self) -> OrderedDict:
        return TargetBalanceRetrieveSerializer(instance=self.instance).data
