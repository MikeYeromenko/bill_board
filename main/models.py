from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal


from main.utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification

user_registrated = Signal(providing_args=['instance'])


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='прошёл активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='слать оповещения о новых комментариях?')
    birth_date = models.DateField(null=True, blank=True)

    class Meta(AbstractUser.Meta):
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def delete(self, using=None, keep_parents=False):
        for bill in self.bills.all():
            bill.delete()
        return AbstractUser.delete(self, using, keep_parents)


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='название')
    order = models.SmallIntegerField(db_index=True, default=0, verbose_name='порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True,
                                     verbose_name='надрубрика')


class SuperRubricManager(models.Manager):

    def get_queryset(self):
        return models.Manager.get_queryset(self).filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'надрубрика'
        verbose_name_plural = 'надрубрики'


class SubRubricManager(models.Manager):

    def get_queryset(self):
        return models.Manager.get_queryset(self).filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return f'{self.super_rubric.name} - {self.name}'

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'подрубрика'
        verbose_name_plural = 'подрубрики'


class Bb(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='рубрика', related_name='bills')
    title = models.CharField(max_length=40, verbose_name='название')
    content = models.TextField(verbose_name='описание')
    price = models.FloatField(default=0, verbose_name='цена')
    contacts = models.TextField(verbose_name='контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='автор объявления',
                               related_name='bills')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='опубликовано')

    def delete(self, using=None, keep_parents=False):
        for ai in self.additional_images.all():
            ai.delete()
        models.Model.delete(self, using, keep_parents)

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'объявление'
        verbose_name_plural = 'объявления'

    def __str__(self):
        return self.title


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, related_name='additional_images',
                           verbose_name='объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='изображение')

    class Meta:
        verbose_name = 'дополнительная иллюстрация'
        verbose_name_plural = 'дополнительные иллюстрации'


class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, related_name='comments', verbose_name='объявление')
    author_name = models.CharField(max_length=30, verbose_name='автор')
    author = models.ForeignKey(AdvUser, on_delete=models.DO_NOTHING, blank=True, related_name='comments',
                               null=True, default=None)
    content = models.TextField(verbose_name='текст комментария')
    is_active = models.BooleanField(default=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, editable=False,
                                      verbose_name='опубликован')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, default=None,
                                       related_name='child_comments', verbose_name='комментарий к комментарию')
    likes = models.SmallIntegerField(default=0, verbose_name='лайки')
    dislikes = models.SmallIntegerField(default=0, verbose_name='дислайки')
    complain = models.BooleanField(default=False, verbose_name='пожаловаться?')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий к объявлению {self.bb.title}'


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


def comment_post_save_dispatcher(sender, **kwargs):
    comment = kwargs['instance']
    author = comment.bb.author
    if kwargs['created'] and author.send_messages and author != comment.author:
        send_new_comment_notification(comment)


user_registrated.connect(user_registrated_dispatcher)
post_save.connect(comment_post_save_dispatcher, sender=Comment)
