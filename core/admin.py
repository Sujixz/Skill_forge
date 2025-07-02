from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Course, Lesson, Enrollment, Progress,BillingDetails


admin.site.register(User, UserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1  


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'description')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')
    list_filter = ('course', 'enrolled_on')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed')
    list_filter = ('completed', 'lesson')



@admin.register(BillingDetails)
class BillingDetailsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'city', 'address','created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'city')