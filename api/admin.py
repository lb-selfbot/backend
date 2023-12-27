from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(PasswordResetToken)
admin.site.register(Order)
admin.site.register(Key)
admin.site.register(CreditKey)
admin.site.register(Transcript)
admin.site.register(Release)
admin.site.register(Log)
admin.site.register(Image)
admin.site.register(FreeTrial)