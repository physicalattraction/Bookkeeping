from django.contrib import admin

from contacts.models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'account', 'email')
    search_fields = ('name', 'account', 'email')
    list_filter = ('name', 'account', 'email')

    fields = ('uuid', 'created_at', 'updated_at', 'name', 'account', 'email')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
