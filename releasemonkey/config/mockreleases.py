class MockRelease(object):
    
    def __init__(self, name, from_revision, to_revision):
        self.name = name
        self.from_revision = from_revision
        self.to_revision = to_revision

class MockReleases(object):
    
    def __init__(self):
        self.rels_in_progress = {}

    def in_progress(self):
        return self.rels_in_progress.values()

    def suggested_release_name(self):
        return "suggested_release"

    def create_release(self, release_name, from_revision, to_revision):
        print "CREATING RELEASE %s %s %s" % (release_name, from_revision, to_revision)
        self.rels_in_progress[release_name] = MockRelease(release_name, from_revision, to_revision)

    def destroy_release(self, release_name):
        print "DESTROYING RELEASE %s %s" % (release_name)
        # should be safe on a no-op
        if release_name in self.rels_in_progress:
            del self.rels_in_progress[release_name]        
        

RELEASES = MockReleases()
