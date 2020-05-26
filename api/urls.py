from rest_framework import routers
from django.urls import path, include


from api.views import BbViewSet


router = routers.DefaultRouter()
router.register('bbs', BbViewSet)


urlpatterns = [
    path('', include(router.urls)),

]
