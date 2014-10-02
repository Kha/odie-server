from django.conf.urls import include, patterns, url
from django.contrib import admin

from odie import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^data/lectures$', views.lectures),
    url(r'^data/lectures/(.+)/documents$', views.documents_of_lecture),
    url(r'^data/examinants$', views.examinants),
    url(r'^data/examinants/(.+)/documents$', views.documents_of_examinant),
    url(r'^data/carts$', views.carts),
    url(r'^data/carts/(.+)$', views.modify_cart),
    url(r'^data/login$', views.login),
    url(r'^data/logout$', views.logout),
    url(r'^data/user$', views.user),
    url(r'^data/print$', views.print_job),
    url(r'^data/log_erroneous_copies$', views.log_erroneous_copies),
    url(r'^data/deposits/(.+)$', views.deposits)
)
