from repo import Revision


class MockRepo(object):
    
    def __init__(self):
        self.tags = {}

    def recent_revisions(self):
        r1 = Revision('234',
                      'ewj',
                      'this is the msg',
                      'http://link')
        r2 = Revision('235',
                      'someone',
                      'this is the msg 2',
                      'http://link2')
        return [r2, r1]

    def untag_release(self, release_name, release_revision):
        print "UNTAGGING: %s %s" % (release_name, release_revision)
        # should be safe on a no-op
        if release_name in self.tags:
            del self.tags[release_name]

    def tag_release(self, release_name, release_revision):
        print "TAGGING: %s %s" % (release_name, release_revision)
        self.tags[release_name] = release_revision

    def last_tagged_revision(self):
        return '201'

    def revisions_between(self, from_revision, to_revision):
        """exclusive / inclusive"""
        return [Revision('100',
                         'ewj',
                         'this is the msg 5',
                         'http://link'),
                Revision('102',
                         'someone',
                         'this is the msg 3',
                         'http://link2')
]

DEBUG = True
SECRET_KEY = 'wingu'
REPO = MockRepo()


