from django.apps import AppConfig
import sys


def _patch_django_context_for_py314():
    if sys.version_info < (3, 14):
        return
    from django.template.context import BaseContext

    def __copy__(self):
        duplicate = self.__class__()
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = __copy__


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):
        _patch_django_context_for_py314()
