import sys

from flask import Flask, g, render_template, redirect, url_for, request

app = Flask(__name__)

@app.before_request
def before_request():
    g.repo = app.config['REPO']
    g.releases = app.config['RELEASES']
    
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

@app.route('/create_release', methods=['POST'])
def create_release():
    releases = g.releases
    repo = g.repo
    
    release_name = request.form['release_name']
    release_revision = request.form['release_revision']
    if release_revision == 'custom':
        release_revision = request.form['custom_revision']

    try:
        repo.tag_release(release_name, release_revision)
        releases.create_release(release_name, release_revision)        
    except Exception as exc:
        # even though technically both of these could not have been
        # created with the exception having been thrown, we don't want
        # implementers to depend on the order of tagging / release
        # creation, so we insist that both untag_release and
        # destroy_release are safe as no-ops if the tag or release
        # doesn't exist, and call them both.
        repo.untag_release(release_name, release_revision)
        releases.destroy_release(release_name, release_revision)
        return render_template('error.html', 
                               error_msg='Could not create the new release.',
                               error_detail=str(exc))

    return redirect(url_for('in_progress'))

if __name__ == '__main__':
    config_module = sys.argv[1]
    app.config.from_object(config_module)
    app.run()
