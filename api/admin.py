from django.contrib import admin
from .models import User, PasswordResetToken, Order, Key, Transcript, Release, Log

admin.site.register(User)
admin.site.register(PasswordResetToken)
admin.site.register(Order)
admin.site.register(Key)
admin.site.register(Transcript)
admin.site.register(Release)
admin.site.register(Log)
