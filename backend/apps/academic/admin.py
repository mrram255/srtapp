from django.contrib import admin
from apps.academic.models import Regulation, Program, Batch, Section, Semester, CurriculumSubject, HolidayCalendar, AcademicEvent

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'program')
    list_filter = ('program',)
    search_fields = ('name', 'program__name')

admin.site.register([Regulation, Section, Semester, CurriculumSubject, HolidayCalendar, AcademicEvent])
