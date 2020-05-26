import datetime

from django.contrib import admin

from main.forms import SubRubricForm
from main.models import AdvUser, SubRubric, SuperRubric, AdditionalImage, Bb, Comment
from main.utilities import send_activation_notification


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
        modeladmin.message_user(request, 'Письма с оповещениями отправлены')


send_activation_notifications.short_description = f'Отправка писем с сообщениями об активации'


class NonActivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('three_days', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'three_days':
            d = datetime.date.today() - datetime.timedelta(days=1)
            return queryset.filter(date_joined__date__lt=d, is_active=False, is_activated=False)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(date_joined__date__lt=d, is_active=False, is_activated=False)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonActivatedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'), 'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)


class SubRubricInline(admin.TabularInline):
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ['super_rubric']
    inlines = [SubRubricInline, ]


class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    fields = (('rubric', 'author'), 'title', 'content', 'price', 'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline, )


class ComplainFilter(admin.SimpleListFilter):
    title = 'Жалобы?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('complained', 'На данный комментарий получены жалобы'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'complained':
            return queryset.filter(complain=True, is_active=True)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('bb', 'created_at', 'complain')
    list_filter = (ComplainFilter,)


admin.site.register(Comment, CommentAdmin)
admin.site.register(AdditionalImage)
admin.site.register(Bb, BbAdmin)
admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(AdvUser, AdvUserAdmin)
