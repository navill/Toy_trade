from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from accounts.models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile

    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]


# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)


# admin.site.register(UserProfile, UserProfileAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'created']


admin.site.register(UserProfile, UserProfileAdmin)

