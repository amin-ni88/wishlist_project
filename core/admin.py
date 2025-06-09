from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WishList, WishListItem, Contribution, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'wallet_balance')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('phone_number', 'bio', 'avatar', 'wallet_balance')}),
    )
    readonly_fields = ('wallet_balance',)

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'occasion_date', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'occasion_date')
    search_fields = ('title', 'owner__username', 'description')
    date_hierarchy = 'created_at'

@admin.register(WishListItem)
class WishListItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'wishlist', 'price', 'status', 'priority', 'created_at')
    list_filter = ('status', 'created_at', 'priority')
    search_fields = ('name', 'description', 'wishlist__title')
    date_hierarchy = 'created_at'

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('item', 'contributor', 'amount', 'is_anonymous', 'created_at')
    list_filter = ('is_anonymous', 'created_at')
    search_fields = ('item__name', 'contributor__username', 'message')
    date_hierarchy = 'created_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'
