"""Read-side composition for the web client; domain mutations live in their modules."""
from apps.users.serializers import UserOutputSerializer
from apps.wallet.services import WalletService
from apps.wallet.serializers import BilleteraSerializer
from apps.openings.inventory import InventoryService
from apps.openings.serializers import ItemInventarioSerializer

def account_snapshot(user):
    inventory = list(InventoryService().list_for_user(user))
    return {
        'user': UserOutputSerializer(user).data,
        'wallet': BilleteraSerializer(WalletService().get_billetera(user)).data,
        'inventory': ItemInventarioSerializer(inventory, many=True).data,
        'aperturas': len(inventory),
    }
