from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Transaction

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('user__username', 'amount')
    date_hierarchy = 'timestamp'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register TransactionAdmin
admin.site.register(Transaction, TransactionAdmin)