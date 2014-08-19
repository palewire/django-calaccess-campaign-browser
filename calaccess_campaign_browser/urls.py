from django.conf.urls import patterns, include, url
from tastypie.api import Api
from django.views.generic.base import RedirectView

from calaccess_campaign_browser.api import FilerResource
from calaccess_campaign_browser import views

v1_api = Api(api_name='v1')
v1_api.register(FilerResource())

urlpatterns = patterns(
    'calaccess_campaign_browser.views',
    url(
        r'^$',
        views.IndexView.as_view(template_name='home/index.html'),
        name='index'
    ),
    url(
        r'^explore$',
        RedirectView.as_view(
            url='/explore/1/',
            permanent=True,
        ),
    ),
    url(
        r'^explore/(?P<page>[\d+]+)/$',
        views.FilerListView.as_view(template_name='filer/list.html'),
        name='filer_list'
    ),
    url(
        r'^filer/(?P<pk>\d+)/$',
        views.FilerDetailView.as_view(template_name='filer/detail.html'),
        name='filer_detail'
    ),
    url(
        r'^committee/(?P<pk>\d+)/contributions/(?P<page>[\d+]+)/$',
        views.CommitteeContributionView.as_view(
            template_name='committee/contribution_list.html'
        ),
        name='committee_contribution_list',
    ),
    url(
        r'^committee/(?P<pk>\d+)/expenditures/(?P<page>[\d+]+)/$',
        views.CommitteeExpenditureView.as_view(
            template_name='committee/expenditure_list.html'
        ),
        name='committee_expenditure_list',
    ),
    url(
        r'^committee/(?P<pk>\d+)/filings/(?P<page>[\d+]+)/$',
        views.CommitteeFilingView.as_view(
            template_name='committee/filing_list.html'
        ),
        name='committee_filing_list',
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
    url(
        r'^contribution/(?P<pk>\d+)/$',
        views.ContributionDetailView.as_view(),
        name='contribution_detail'
    ),
    url(
        r'^expenditure/(?P<pk>\d+)/$',
        views.ExpenditureDetailView.as_view(),
        name='expenditure_detail',
    ),
    url(
        r'^search/$', views.search, name='search'
    ),
    # API
    url(r'^api/', include(v1_api.urls)),

)
