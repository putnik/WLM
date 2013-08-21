# -*- encoding: utf-8 -*-
import cookielib, urllib, urllib2
import json
import re

from datetime import datetime
from dateutil.parser import parse
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from wlm.models import Region, City, Monument, MonumentPhoto
from settings import WIKI_NAME, WIKI_PASSWORD


class Command(BaseCommand):
    help = u'Export cultural heritage into Wikipedia'


    def handle(self, *args, **options):
        regions = Region.objects.all()

        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        self.login()
        for region in regions:
            monuments = Monument.objects.filter(region_id=region.id)
            cities = City.objects.filter(region_id=region.id)
            for city in cities:
                monuments_city = Monument.objects.filter(region_id=region.id, city_id=city.id)
                if len(monuments_city) > 10:
                    city_page = '%s/%s' % (region.name, city.name);
                    if self.update_page(city_page, monuments_city):
                        monuments = monuments.exclude(city_id=city.id)

            self.update_page(region.name, monuments)

        self.stdout.write(u'Successfully exported all cultural heritage objects\n')


    def update_page(self, title, monuments):
        print('%s - %d' % (title, len(monuments)))
        if not len(monuments):
            return False
        if len(monuments) > 330:
            for i in range(0, len(monuments) / 300):
                self.update_page('%s/%d' % (title, i + 1), monuments[i:i+300])
            self.update_page('%s/%d' % (title, i + 2), monuments[i+300:len(monuments)])
            return True
        text = u'{{WLM/заголовок}}\n'
        for m in monuments:
            city_name = u''
            if m.city and m.city.name:
                city_name = m.city.name
            text += u'{{WLM/строка\n'
            text += u'| id = %s\n' % m.kult_id
            text += u'| название = %s\n' % m.name
            text += u'| нп = %s\n' % city_name
            text += u'| адрес = %s\n' % m.address
            text += u'| регион = %s\n' % m.region
            text += u'| lat = %s\n' % m.coord_lat
            text += u'| lon = %s\n' % m.coord_lon
            text += u'| фото = \n'
            text += u'}}\n'
        text += u'|}'

        page = u'Проект:Вики любит памятники/Списки/%s' % title
        api_params = {
            'action': 'query',
            'prop': 'info',
            'intoken': 'edit',
            'titles': page.encode('utf8'),
        }
        answer = self.api_request(api_params)
        pages = answer['query']['pages']
        for page_id in pages:
            token = pages[page_id]['edittoken']
            break

        api_params = {
            'action': 'edit',
            'summary': u'автоматическое обновление списка'.encode('utf8'),
            'bot': 1,
            'title': page.encode('utf8'),
            'text': text.encode('utf8'),
            'token': token,
        }
        answer = self.api_request(api_params, True)
        
        return True


    def login(self):
        api_params = {
            'action': 'login',
            'lgname': WIKI_NAME.encode('utf8'),
            'lgpassword': WIKI_PASSWORD.encode('utf8'),
        }
        answer = self.api_request(api_params, True)

        api_params['lgtoken'] = answer['login']['token']
        answer = self.api_request(api_params, True)
        
        return True


    def api_request(self, ext_params, post=False):
        params = {
            'format': 'json',
        }
        params.update(ext_params)
        get_string = urllib.urlencode(params)

        server = 'http://ru.wikipedia.org'

        if post:
            f = self.opener.open('%s/w/api.php' % server, get_string)
        else:
            f = self.opener.open('%s/w/api.php?%s' % (server, get_string))

        return json.load(f)

