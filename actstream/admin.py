from django.contrib import admin
from django.contrib.admin.actions import delete_selected

from actstream.models import Action, Follow

class ActionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('__unicode__','actor','verb','target', 'object')
    list_editable = ('verb',)
    list_filter = ('timestamp',)

class FollowAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','user','actor')
    list_editable = ('user',)
    list_filter = ('user',)
    ordering = ('user', 'object_id')
    actions = [delete_selected]

admin.site.register(Action, ActionAdmin)
admin.site.register(Follow, FollowAdmin)
