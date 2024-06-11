from rest_framework.routers import SimpleRouter

from server.views.api import gameserver

app_name = "server"
router = SimpleRouter()
router.register(r"gameserver", gameserver.UserGameserverViewSet, basename="gameserver")

urlpatterns = router.urls
