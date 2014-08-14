from django.conf.urls import patterns, include, url
from tastypie.api import Api

from campaign_finance.api import FilerResource
from campaign_finance import views

v1_api = Api(api_name='v1')
v1_api.register(FilerResource())

urlpatterns = patterns(
    'campaign_finance.views',
    url(
        r'^$',
        views.IndexView.as_view(template_name='home/index.html'),
        name='index'
    ),
    url(
        r'^filer/(?P<pk>\d+)/$',
        views.FilerDetailView.as_view(template_name='filer/detail.html'),
        name='filer_detail'
    ),
    url(
        r'^committee/(?P<pk>\d+)/$',
        (
            views.
            CommitteeDetailView
            .as_view(
                template_name='committee/detail.html'
            )
        ),
        name='committee_detail'
    ),
    url(
        r'^filing/(?P<pk>\d+)/$',
        views.FilingDetailView.as_view(template_name='filing/detail.html'),
        name='filing_detail'
    ),

    # API
    url(r'^api/', include(v1_api.urls)),

)
