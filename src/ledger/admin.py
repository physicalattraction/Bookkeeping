from django.contrib import admin

from ledger.models import Ledger, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'date', 'description', 'invoice_number', 'debit_account', 'credit_account', 'amount',)
    search_fields = ('description', 'invoice_number', 'contact',)
    list_filter = ('debit_account', 'credit_account', 'contact')

    fields = ('uuid', 'created_at', 'updated_at', 'date', 'description', 'invoice_number',
              'contact', 'debit_account', 'credit_account', 'amount')
    readonly_fields = ('uuid', 'created_at', 'updated_at')


class TransactionInline(admin.TabularInline):
    model = Transaction
    show_change_link = True
    extra = 4


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = ('year',)

    fields = ('year',)
    inlines = (TransactionInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by('year')
        return queryset
