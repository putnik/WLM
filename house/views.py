from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.db.models import Count, Max, Min
from house.models import Street, House


def street_list(request):
    s_list = Street.objects.order_by('name').annotate(house_count=Count('house'))

    return render_to_response('house/street_list.html', {
        'list': s_list,
        }, context_instance=RequestContext(request))


def street(request, id):
    s = Street.objects.get(pk=id)
    h_list = House.objects.filter(street=id).order_by('number')
    map_border = h_list.aggregate(Max('coord_x'), Min('coord_x'), Max('coord_y'), Min('coord_y'))
    if map_border['coord_y__max'] != None:
        map_center = {
            'lat': (map_border['coord_y__max'] + map_border['coord_y__min']) / 2,
            'long': (map_border['coord_x__max'] + map_border['coord_x__min']) / 2,
        }
    else:
        map_center = False

    return render_to_response('house/street.html', {
        'street': s,
        'list': h_list,
        'map_center': map_center,
        'CMADE_KEY': settings.CMADE_KEY,
        }, context_instance=RequestContext(request))


def house(request, id):
    h = House.objects.get(pk=id)

    return render_to_response('house/house.html', {
        'house': h,
        'CMADE_KEY': settings.CMADE_KEY,
        }, context_instance=RequestContext(request))

