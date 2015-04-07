from tastypie.resources import ModelResource, ALL
from .models import Filer, Filing
from .utils.serializer import CIRCustomSerializer


class FilerResource(ModelResource):
    class Meta:
        queryset = Filer.objects.all()
        serializer = CIRCustomSerializer()
        filtering = {'filer_id_raw': ALL}
        excludes = ['id']


class FilingResource(ModelResource):
    class Meta:
        queryset = Filing.objects.all()
        serializer = CIRCustomSerializer()
        filtering = {'filing_id_raw': ALL}
        excludes = ['id']
