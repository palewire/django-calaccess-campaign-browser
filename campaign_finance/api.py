from tastypie.resources import ModelResource
from .models import Filer, Committee, Filing

class FilerResource(ModelResource):
    class Meta:
        queryset = Filer.objects.all()