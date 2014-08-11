from tastypie.resources import ModelResource
from .models import Filer, Committee, Filing
from .utils.serializer import CIRCustomSerializer


class FilerResource(ModelResource):
    class Meta:
        queryset = Filer.objects.all()
        serializer = CIRCustomSerializer()
