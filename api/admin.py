from django.contrib import admin
from .models import User, PasswordResetToken, Order, Key

admin.site.register(User)
admin.site.register(PasswordResetToken)
admin.site.register(Order)
admin.site.register(Key)
