

from applications.getdata.models import Proyecto


class SemaforoMixin:
    
    def __init__(self, project):

        self.project = Proyecto.objects.all().order_by('-id').first()
        