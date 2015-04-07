from django.conf.urls import patterns, include, url
from tastypie.api import Api
from django.views.generic.base import RedirectView
from calaccess_campaign_browser.api import FilerResource, FilingResource
from calaccess_campaign_browser import views
from calaccess_campaign_browser.views import search
from django.views.generic import TemplateView

# Set up the endpoints for the REST service.
#
# Usage:
#
#    http://<hostname>:<port>//api/v1/
#    http://<hostname>:<port>//api/v1/filer/
#    http://<hostname>:<port>//api/v1/filing/?filing_id_raw=1852192'
#
v1_api = Api(api_name='v1')
v1_api.register(FilerResource())
v1_api.register(FilingResource())

# Set up the endpoints for the web application.
#
urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url='/latest/', permanent=False)),
    url(
        r'^latest/$',
        views.LatestFilingView.as_view(),
        name='latest_list'
    ),
    url(
        r'^filers/$',
        RedirectView.as_view(url='/filers/1/', permanent=False),
        name="filer_list"
    ),
    url(
        r'^filers/(?P<page>[\d+]+)/$',
        views.FilerListView.as_view(),
        name='filer_page'
    ),
    url(
        r'^filer/(?P<pk>\d+)/$',
        views.FilerDetailView.as_view(),
        name='filer_detail'
    ),
    url(
        r'^committee/(?P<pk>\d+)/contributions/(?P<page>[\d+]+)/$',
        views.CommitteeContributionView.as_view(),
        name='committee_contribution_list',
    ),
    url(
        r'^committee/(?P<pk>\d+)/expenditures/(?P<page>[\d+]+)/$',
        views.CommitteeExpenditureView.as_view(),
        name='committee_expenditure_list',
    ),
    url(
        r'^committee/(?P<pk>\d+)/filings/(?P<page>[\d+]+)/$',
        views.CommitteeFilingView.as_view(),
        name='committee_filing_list',
    ),
    url(
        r'^committee/(?P<pk>\d+)/$',
        views.CommitteeDetailView.as_view(),
        name='committee_detail'
    ),
    url(
        r'^filing/(?P<pk>\d+)/$',
        views.FilingDetailView.as_view(),
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
    url(r'^search/$', search.SearchList.as_view(), name='search-list'),
    url(
        r'^search/contribs-by-name/$',
        search.search_contribs_by_name,
        name='search-contribs-by-name'
    ),
    url(
        r'^parties/$',
        views.PartyListView.as_view(),
        name='party_list'
    ),

    # API
    url(r'^api/', include(v1_api.urls)),

    url(
        r'^robots\.txt$',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain')
    ),
)
