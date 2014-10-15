import re
from django.db.models import Q
from django.views.generic import TemplateView
from django.shortcuts import render
from calaccess_campaign_browser.models import Contribution

findterms = re.compile(r'"([^"]+)"|(\S+)').findall
normspace = re.compile(r'\s{2,}').sub


class SearchList(TemplateView):
    template_name = "calaccess_campaign_browser/search_list.html"


def normalize_query(query_string,):
    """
    Splits the query string in invidual keywords, getting rid of unecessary
    spaces and grouping quoted words together.

    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """
    return [
        normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)
    ]


def get_query(query_string, search_fields):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search_contribs_by_name(request):
    query_string = ''
    results = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        query = get_query(query_string, [
            'contributor_city', 'contributor_zipcode',
            'contributor_first_name', 'contributor_last_name',
            'contributor_employer', 'contributor_occupation'
        ])
        results = Contribution.real.filter(query).order_by("-date_received")
    context = {
        'query_string': query_string,
        'results': results
    }
    template = 'calaccess_campaign_browser/search_contribs_by_name.html'
    return render(request, template, context)
