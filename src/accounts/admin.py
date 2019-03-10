from django.contrib import admin

from accounts.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'debit_type')
    search_fields = ('code', 'name', 'debit_type')
    list_filter = ('type', 'debit_type')

    fields = ('code', 'name', 'type', 'debit_type')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by('name')
        return queryset
