from rest_framework import serializers

from main.models import Bb


class BbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bb
        exclude = []



    # rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='рубрика', related_name='bills')
    # title = models.CharField(max_length=40, verbose_name='название')
    # content = models.TextField(verbose_name='описание')
    # price = models.FloatField(default=0, verbose_name='цена')
    # contacts = models.TextField(verbose_name='контакты')
    # image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='изображение')
    # author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='автор объявления',
    #                            related_name='bills')
    # is_active = models.BooleanField(default=True, db_index=True, verbose_name='выводить в списке?')
    # created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='опубликовано')
