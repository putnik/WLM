# -*- encoding: utf-8 -*-
import urllib, urllib2
import json
import re

from datetime import datetime
from dateutil.parser import parse
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from wlm.models import Region, Monument, MonumentPhoto
from settings import WIKI_NAME, WIKI_PASSWORD


class Command(BaseCommand):
    help = u'Export cultural heritage into Wikipedia'
    cookie = ''


    def handle(self, *args, **options):
        regions = Region.objects.all()
        self.login()
        for region in regions:
            print '%s (%s): ' % (region.name, region.id)
            monuments = Monument.objects.filter(region_id=region.id)
            if self.update_page(region.name, monuments):
                print 'OK\n'
            else:
                print 'fail!\n'

        self.stdout.write(u'Successfully exported all cultural heritage objects\n')


    def update_page(self, title, monuments):
        if not len(monuments) or len(monuments) > 500:
            return False
        text = u'{{WLM/заголовок}}\n'
        for m in monuments:
            text += u'{{WLM/строка\n'
            text += u'| id = %s\n' % m.kult_id
            text += u'| название = %s\n' % m.name
            text += u'| нп = %s\n' % m.city.name
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
        print answer
        
        return True


    def login(self):
        api_params = {
            'action': 'login',
            'lgname': WIKI_NAME.encode('utf8'),
            'lgpassword': WIKI_PASSWORD.encode('utf8'),
        }
        answer = self.api_request(api_params, True)

        token = answer['login']['token']
        api_params['lgtoken'] = token

        sessionid = answer['login']['sessionid']
        self.cookie = 'ruwikiSession=%s' % sessionid

        answer = self.api_request(api_params, True)
        prefix = answer['login']['cookieprefix']
        cookie = '%sUserID=%s' % (prefix, answer['login']['lguserid'])
        cookie += '; %sUserName=%s' % (prefix, answer['login']['lgusername'])
        cookie += '; %sSession=%s' % (prefix, answer['login']['sessionid'])
        self.cookie = cookie
        
        return True


    def api_request(self, ext_params, post=False):
        params = {
            'format': 'json',
        }
        params.update(ext_params)
        get_string = urllib.urlencode(params)

        server = 'http://ru.wikipedia.org'

        if post:
            req = urllib2.Request(url='%s/w/api.php' % server, data=get_string)
        else:
            req = urllib2.Request(url='%s/w/api.php?%s' % (server, get_string))

        if self.cookie:
            req.add_header('Cookie', self.cookie)

        f = urllib2.urlopen(req)

        return json.load(f)

