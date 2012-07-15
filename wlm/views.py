from django.db import connection
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from wlm.models import City, Monument, HousePhoto


def index_page(request):
    h_list = Monument.objects.exclude(coord_lon=None).select_related()
    h_list = h_list.filter(city_id=34)
    p_list = HousePhoto.objects.all()[:30]

    return render_to_response('house/index.html', {
        'house_list': h_list,
        'photo_list': p_list,
        'cities': City.objects.values('id', 'name').all(),
        'CMADE_KEY': settings.CMADE_KEY,
        }, context_instance=RequestContext(request))


def upload(request):
    h_list = Monument.objects.all()

    return render_to_response('house/upload.html', {
        'house_list': h_list,
        'CMADE_KEY': settings.CMADE_KEY,
        }, context_instance=RequestContext(request))


def add(request):
    h_list = Monument.objects.all()
    p_list = HousePhoto.objects.all()[:30]

    return render_to_response('house/add.html', {
        'house_list': h_list,
        'photo_list': p_list,
        'CMADE_KEY': settings.CMADE_KEY,
        }, context_instance=RequestContext(request))



def house(request, id):
    h = Monument.objects.get(pk=id)
    photo = HousePhoto.objects.filter(house=h)[:30]

    return render_to_response('house/house.html', {
        'house': h,
        'photo': photo,
        'is_admin': True,
        'CMADE_KEY': settings.CMADE_KEY,
        }, context_instance=RequestContext(request))

def coordinates_doubled(request):
    query = '''select count(id), coord_lat, coord_lon from wlm_monument
        group by coord_lat, coord_lon
        having count(id) > 1;'''
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return render_to_response('coord_doubles.html', {'doubles':rows,})

def monuments_double_coordinates(request):
    if request.GET['lat']:
        lat = float(request.GET.get('lat'))
    else:
        lat = None
    if request.GET['lon']:
        lon = float(request.GET.get('lon'))
    else:
        lon = None
    monuments = Monument.objects.filter(coord_lat=lat, coord_lon=lon)
    return render_to_response('monuments_double.html', {'monuments': monuments,})
