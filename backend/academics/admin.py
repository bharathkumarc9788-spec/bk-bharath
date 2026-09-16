from django.contrib import admin

from .models import (AttendanceRecord, ClassSection, Department, Exam,
                     ExamSchedule, LeaveRequest, MarkEntry, ParentProfile,
                     Subject, TeacherAttendance, TeacherProfile, TimetableEntry)

admin.site.register([
    Department, Subject, TeacherProfile, TeacherAttendance, LeaveRequest,
    ParentProfile, ClassSection, TimetableEntry, AttendanceRecord,
    Exam, ExamSchedule, MarkEntry,
])