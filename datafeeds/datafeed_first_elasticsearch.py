import base64
import json
import logging

from google.appengine.api import urlfetch

from consts.event_type import EventType
from datafeeds.datafeed_base import DatafeedBase

from models.event_team import EventTeam

from parsers.first_elasticsearch.first_elasticsearch_event_list_parser import FIRSTElasticSearchEventListParser
from parsers.first_elasticsearch.first_elasticsearch_team_details_parser import FIRSTElasticSearchTeamDetailsParser


class DatafeedFIRSTElasticSearch(object):
    def __init__(self):
        URL_BASE = 'http://es01.usfirst.org'
        self.EVENT_LIST_URL_PATTERN = URL_BASE + '/events/_search?size=1000&source={"query":{"query_string":{"query":"(event_type:FRC)%%20AND%%20(event_season:%s)"}}}'  # (year)
        # self.EVENT_DETAILS_URL_PATTERN = URL_BASE + '/events/_search?size=1&source={"query":{"query_string":{"query":"_id:%s"}}}'  # (first_eid)
        self.EVENT_TEAMS_URL_PATTERN = URL_BASE + 'search?size=1000&source={"_source":{"exclude":["awards","events"]},"query":{"query_string":{"query":"events.fk_events:%s%%20AND%%20profile_year:%s}}}'  # (first_eid, year)
        # self.TEAM_DETAILS_URL_PATTERN = URL_BASE + '/teams/_search?size=1&source={"query":{"query_string":{"query":"_id:%s"}}}'  # (first_tpid)

    def _get_event_short(self, event_short):
        return self.EVENT_SHORT_EXCEPTIONS.get(event_short, event_short)

    def _parse(self, url, parser):
        headers = {
        }
        try:
            result = urlfetch.fetch(url,
                                    headers=headers,
                                    deadline=5)
        except Exception, e:
            logging.error("URLFetch failed for: {}".format(url))
            logging.info(e)
            return None

        if result.status_code == 200:
            return parser.parse(json.loads(result.content))
        else:
            logging.warning('URLFetch for %s failed; Error code %s' % (url, result.status_code))
            return None

    def getEventList(self, year):
        events = self._parse(self.EVENT_LIST_URL_PATTERN % (year), FIRSTElasticSearchEventListParser(year))
        return events

    # TODO: implement
    # def getEventDetails(self, event):
    #     return

    def getEventTeams(self, event):
        teams = self._parse(self.EVENT_TEAMS_URL_PATTERN % (event.first_eid, event.year), FIRSTElasticSearchTeamDetailsParser(event.year))
        return teams

    # TODO: implement
    # def getTeamDetails(self, team):
        # return
