from django.contrib import admin
from .models import Parent, ParentFeedback, Teacher, TeacherFeedback

admin.site.register([Teacher, Parent, TeacherFeedback, ParentFeedback])