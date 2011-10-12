from subprocess import Popen, PIPE
import os

from repo import Revision

class SvnRepo(object):
    
    def __init__(self, repo, uname, password):
        self.repo = repo
        self.uname = uname
        self.password = password
        pass

    def recent_revisions(self):
        # no op for the moment
        return []

    def untag_release(self, release_name, release_revision):
        # no op for the moment
        pass

    def tag_release(self, release_name, release_revision):
        # no op for the moment
        pass

    def last_tagged_revision(self):
        # no op for the moment
        return None

    def revisions_between(self, from_revision, to_revision):
        svn_cmd = "/usr/bin/env svn log --no-auth-cache --username %s --password %s -r %s:%s %s" % (self.uname, self.password, from_revision, to_revision, self.repo)
        svn_cmd = svn_cmd.split()
        pid = Popen(svn_cmd, stdout=PIPE)
        log = pid.communicate()[0]
        sep = '------------------------------------------------------------------------'
        entries = log.split(sep)

        revs = []

        for entry in entries:
            if not entry:
                continue
            # first line is blank, who needs it?
            lines = entry.split('\n')[1:]
            header = lines[0]
            if not header:
                continue
            rev, author, date, num_comment_lines = [x.strip() for x in header.split('|')]
            rev = rev[1:]
            if rev != from_revision:
                revs.append(Revision(rev, author, '\n'.join(lines[1:]), 'none'))
        
        return revs

REPO = SvnRepo(os.environ['RELEASEMONKEY_REPO'], os.environ['RELEASEMONKEY_UNAME'], os.environ['RELEASEMONKEY_PASSWORD'])

