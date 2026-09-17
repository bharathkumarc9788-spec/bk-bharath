"""Django admin registrations for ERP models."""

from django.contrib import admin

from .models import (AcademicYear, Announcement, Employee, FeePayment,
                     FeeStructure, Holiday, Homework, HomeworkSubmission,
                     Hostel, HostelAllocation, HostelRoom, House,
                     InventoryCategory, InventoryItem, InventoryMovement,
                     PetRecord, SchoolBoard, SchoolProfile)

admin.site.register(SchoolProfile)
admin.site.register(AcademicYear)
admin.site.register(SchoolBoard)
admin.site.register(House)
admin.site.register(Holiday)
admin.site.register(Homework)
admin.site.register(HomeworkSubmission)
admin.site.register(PetRecord)
admin.site.register(FeeStructure)
admin.site.register(FeePayment)
admin.site.register(Hostel)
admin.site.register(HostelRoom)
admin.site.register(HostelAllocation)
admin.site.register(Employee)
admin.site.register(InventoryCategory)
admin.site.register(InventoryItem)
admin.site.register(InventoryMovement)
admin.site.register(Announcement)