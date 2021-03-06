from pyramid import testing

from votabo.models import DBSession, Tag
from votabo.tests import VotaboTest
from votabo.views.tag import tag_list


class test_tag_list(VotaboTest):
    def setUp(self):
        VotaboTest.setUp(self)
        DBSession.add(Tag.get_or_create(u"apple"))
        DBSession.add(Tag.get_or_create(u"bacon"))
        DBSession.add(Tag.get_or_create(u"cat"))
        DBSession.add(Tag.get_or_create(u"kitten"))
        DBSession.add(Tag.get_or_create(u"pie"))
        DBSession.add(Tag.get_or_create(u"!!!"))

    def test_basic(self):
        request = testing.DummyRequest()
        info = tag_list(request)
        info["tags"] = list(info["tags"])
        self.assertDictEqual(info, {
            'starts_with': "a",
            'tags_min': 1,
            "tags": [
                {"name": "apple", "count": 1}
            ]
        })

    # postgres only
#    def test_misc(self):
#        request = testing.DummyRequest(GET={"tags_min": "1", "starts_with": "?"})
#        info = tag_list(request)
#        info["tags"] = list(info["tags"])
#        self.assertDictEqual(info, {
#            'starts_with': "?",
#            'tags_min': 1,
#            "tags": [
#                {"name": "!!!", "count": 1}
#            ]
#        })

    def test_min(self):
        request = testing.DummyRequest(GET={"tags_min": 12})
        info = tag_list(request)
        info["tags"] = list(info["tags"])
        self.assertDictEqual(info, {
            'starts_with': "a",
            'tags_min': 12,
            "tags": [
            ]
        })
