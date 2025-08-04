from django.contrib import admin
from .models import Subjects, Classrooms, Teachers

class SubjectsAdmin(admin.ModelAdmin):
    list_display = ('id','title','lectures','studies','praktical_work','hardness')
    list_display_links = ('id','title')

class ClassroomsAdmin(admin.ModelAdmin):
    list_display = ('id','number','lectures','studies','praktical_work','available_on_monday','available_on_tuesday','available_on_wednesday','available_on_thursday','available_on_friday')
    list_display_links = ('id','number')

class TeachersAdmin(admin.ModelAdmin):
    list_display = ('id','name','subject', 'lectures', 'studies', 'praktical_work', 'available_on_monday','available_on_tuesday','available_on_wednesday','available_on_thursday','available_on_friday')
    list_display_links = ('id','name')

admin.site.register(Subjects,  SubjectsAdmin)
admin.site.register(Classrooms,ClassroomsAdmin)
admin.site.register(Teachers,  TeachersAdmin)
