from flask import Flask, g, render_template, redirect, url_for


class Revision(object):

    def __init__(self, 
                 revision,
                 author,
                 msg,
                 link):
        self.revision = revision
        self.author = author
        self.msg = msg
        self.link = link

    def format_short_msg(self):
        return "%s %s" % (self.author, self.msg)


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


class MockReleases(object):
    
    def in_progress(self):
        return None

    def suggested_release_name(self):
        return "the new release"

DEBUG = True
SECRET_KEY = 'wingu'
REPO = MockRepo
RELEASES = MockReleases

app = Flask(__name__)

app.config.from_object(__name__)

@app.before_request
def before_request():
    g.repo = REPO()
    g.releases = RELEASES()
    
@app.route('/')
def home():
    return render_template('home.html', 
                           repo=g.repo,
                           in_progress_release=g.releases.in_progress())

@app.route('/new_release')
def new_release():
    repo = g.repo
    releases = g.releases
    
    suggested_release_name = releases.suggested_release_name()
    recent_revisions = repo.recent_revisions()
    
    return render_template('new_release.html',
                           suggested_release_name=suggested_release_name,
                           recent_revisions=recent_revisions)

@app.route('/old_releases')
def old_releases():
    return render_template('old_releases.html')

@app.route('/in_progress')
def in_progress():
    in_progress_release = g.releases.in_progress()
    if not in_progress_release:
        return render_template('no_in_progress.html')
    return render_template('in_progress.html')

@app.route('/create_release')
def create_release():
    return redirect(url_for('in_progress'))

if __name__ == '__main__':
    app.run()
