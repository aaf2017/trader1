from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home"),                                          #localhost:8000/ ->views.home()
    path('getStockInfo/<symbol>', views.getStockInfo, name="stockInfo"),        #localhost:8000/ ->views.getStockInfo()
    path('trade', views.trade, name="trade"),                                   #localhost:8000/ ->views.trade()
    path('login', views.login_user, name="login"),                              #localhost:8000/login ->views.login_user()
    path('logout', views.logout_user, name="logout"),                           #localhost:8000/logout ->views.logout_user()
    path('register', views.register_user, name="register"),                     #localhost:8000/register ->views.register_user()
    path('edit_profile', views.edit_profile, name="edit_profile"),              #localhost:8000/edit_profile ->views.edit_profile()
    path('change_password', views.change_password, name="change_password"),     #localhost:8000/edit_profile ->views.edit_profile()
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    

