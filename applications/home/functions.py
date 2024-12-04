

from applications.getdata.models import Proyecto


def get_last_project():
    """
    Obtiene el último proyecto de la base de datos.
    """
    return Proyecto.objects.all().order_by('-id').first()