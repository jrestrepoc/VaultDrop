from django.test import TestCase
from apps.cases.models import Item
from apps.cases.serializers import ItemSerializer

class CatalogImageTests(TestCase):
    def test_images_follow_database_identity_after_reordering(self):
        knife = Item.objects.create(nombre='Karambit', imagen_url='/static/knife.png')
        rifle = Item.objects.create(nombre='AK-47', imagen_url='/static/rifle.png')
        for sequence in ([knife, rifle], [rifle, knife]):
            rows = ItemSerializer(sequence, many=True).data
            self.assertEqual({row['id']:row['imagen_url'] for row in rows}, {knife.id:'/static/knife.png',rifle.id:'/static/rifle.png'})
