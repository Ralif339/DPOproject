from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Course)
admin.site.register(CommissionMember)
admin.site.register(StudentExpulsion)
admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(StudentGroup)
admin.site.register(GroupCommission)
admin.site.register(Statements)