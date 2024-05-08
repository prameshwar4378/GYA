 
from django.contrib import admin
from django.urls import path,include
from AdminApp.views import register,verify_otp, login_with_otp,user_login,membership_payment
from Website.views import index

from AdminApp import urls as AdminUrls
from  UserApp import urls as UserUrls
from  Website import urls as WebsiteUrls

from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('default_admin/', admin.site.urls),
    path('', index, name='index' ),
    path('admin/', include(AdminUrls)),
    path('user/', include(UserUrls)),
    path('web/', include(WebsiteUrls)),
    path('verify_otp/', verify_otp, name="verify_otp"),
    path('login/', user_login, name="user_login"),
    path('login_otp/', login_with_otp, name="login_with_otp"),
    path('register/', register, name="register"),
    path('membership_payment/', membership_payment, name="membership_payment"),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
