from repo import Revision
        


class MockRepo(object):
    
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

    def tag_release(self, release_name, release_revision):
        print "TAGGING: %s %s" % (release_name, release_revision)


class MockReleases(object):
    
    def in_progress(self):
        return None

    def suggested_release_name(self):
        return "the new release"

    def create_release(self, release_name, release_revision):
        raise Exception("already current release")
        print "CREATING RELEASE %s %s" % (release_name, release_revision)

    def destroy_release(self, release_name, release_revision):
        print "DESTROYING RELEASE %s %s" % (release_name, release_revision)


DEBUG = True
SECRET_KEY = 'wingu'
REPO = MockRepo()
RELEASES = MockReleases()
