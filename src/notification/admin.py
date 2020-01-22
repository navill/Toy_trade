from django.contrib import admin

# Register your models here.
from notification.models import Action


class ActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'verb', 'content_object', 'created']
    list_filter = ['created']
    search_fields = ['verb']


admin.site.register(Action, ActionAdmin)
