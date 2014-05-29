from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Lushu.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^images/', include('images.urls')),
)

urlpatterns += patterns('Lushu.views',
    (r"^$", "homePage"),
    (r"^home/$", "homePage"),
    (r"^selSights/$", "selSights"),
    (r"^datePlanning/$", "datePlanning"),
    (r"^detailPlanning/$", "detailPlanning"),
    (r"^getPlan/$", "getPlan"),
)
