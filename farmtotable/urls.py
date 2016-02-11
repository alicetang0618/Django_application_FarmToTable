from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login, logout
import settings

urlpatterns = patterns('',
    url(r'^$', 'applications.views.intro', name='intro'),
    url(r'^home/$', 'applications.views.home', name = 'home'),
    url(r'^register/$', 'applications.views.register', name = 'register'),
    url(r'^login/$', 'applications.views.login', name = 'login'),
    url(r'^logout/$', 'applications.views.logout', name='logout'),
    url(r'^add_product/$', 'applications.views.add_product', name='add_product'),
    url(r'^demand/$', 'applications.views.demand', name = 'demand'), 
    url(r'^my_products/$', 'applications.views.my_products', name = 'my_products'),
    url(r'^product/(?P<product_id>\d+)/$', 'applications.views.product', name = 'product'), 
    url(r'^modify_product/(?P<product_id>\d+)/$', 'applications.views.modify_product', name = 'modify_product'), 
    url(r'^modify_profile/$', 'applications.views.modify_profile', name = 'modify_profile'), 
    url(r'^add_to_cart/(?P<product_id>\d+)/$', 'applications.views.add_to_cart', name = 'add_to_cart'), 
    url(r'^shopping_cart/$', 'applications.views.shopping_cart', name = 'shopping_cart'), 
    url(r'^item/(?P<item_id>\d+)/$', 'applications.views.item', name = 'item'), 
    url(r'^modify_item/(?P<item_id>\d+)/$', 'applications.views.modify_item', name = 'modify_item'),     
    url(r'^verify_order/(?P<order_id>\d+)/$', 'applications.views.verify_order', name = 'verify_order'),   
    url(r'^checkout/$', 'applications.views.checkout', name = 'checkout'),  
    url(r'^search/(?P<search_id>\d+)$','applications.views.search',name='search'),
    url(r'^order_success/$','applications.views.order_success',name='order_success'),
    url(r'^error_account/$','applications.views.error_account',name='error_account'),
    url(r'^error_quant/(?P<item_id>\d+)/$','applications.views.error_quant',name='error_quant'),
    url(r'^my_orders/$','applications.views.my_orders',name='my_orders'),
    url(r'^order/(?P<order_id>\d+)/$','applications.views.order',name='order'),
    url(r'^my_profile/$','applications.views.my_profile',name='my_profile'),
    url(r'^profile/(?P<user_id>\d+)/$','applications.views.profile',name='profile'),
    url(r'^my_messages/$','applications.views.my_messages',name='my_messages'),
    url(r'^discussion/$','applications.views.discussion',name='discussion'),
    url(r'^recommend/$','applications.views.recommend',name='recommend'),
    url(r'^best_seller/$','applications.views.best_seller',name='best_seller'),
    url(r'^like/$', 'applications.views.like', name='like'),
    url(r'^message/(?P<message_id>\d+)/$','applications.views.message',name='message'),
    url(r'^spend_categories\.svg$', 'applications.views.spend_categories', name='spend_categories'),
    url(r'^finance/$','applications.views.finance',name='finance'),
    url(r'^revenue_categories\.svg$', 'applications.views.revenue_categories', name='revenue_categories'),
    #functional
    url(r'session_security/', include('session_security.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #footer urls
    url(r'^contactus/$', 'applications.views.contactus', name = 'contactus'), 
    url(r'^aboutus/$', 'applications.views.aboutus', name = 'aboutus'), 
    url(r'^career/$', 'applications.views.career', name = 'career'), 
    url(r'^ourteam/$', 'applications.views.ourteam', name = 'ourteam'), 

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
