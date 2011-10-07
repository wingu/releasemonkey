import sys

from flask import Flask, g, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

@app.before_request
def before_request():
    g.repo = app.config['REPO']
    g.releases = app.config['RELEASES']

@app.teardown_request
def teardown_request(exception=None):
    teardowns = []
    if 'TEARDOWNS' in app.config:
        eardowns = app.config['TEARDOWNS']
    for teardown in teardowns:
        teardown()
    
@app.route('/')
def home():
    return render_template('home.html', 
                           repo=g.repo,
                           in_progress_releases=g.releases.in_progress())

@app.route('/new_release')
def new_release():
    repo = g.repo
    releases = g.releases
    
    suggested_release_name = releases.suggested_release_name()
    recent_revisions = repo.recent_revisions()
    from_revision = repo.last_tagged_revision()
    
    return render_template('new_release.html',
                           suggested_release_name=suggested_release_name,
                           recent_revisions=recent_revisions,
                           from_revision=from_revision)

@app.route('/old_releases')
def old_releases():
    return render_template('old_releases.html')

@app.route('/in_progress')
def in_progress():
    in_progress_releases = g.releases.in_progress()
    if not in_progress_releases:
        return render_template('no_in_progress.html')
    return render_template('in_progress.html',
                           in_progress_releases=in_progress_releases)

@app.route('/create_release', methods=['POST'])
def create_release():
    releases = g.releases
    repo = g.repo

    release_name = request.form['release_name']
    to_revision = request.form['to_revision']
    from_revision = request.form['from_revision']
    if to_revision == 'custom':
        to_revision = request.form['custom_revision']

    try:
        repo.tag_release(release_name, to_revision)
        commits = repo.revisions_between(from_revision, to_revision)
        releases.create_release(release_name, 
                                from_revision, 
                                to_revision, 
                                commits)
    except Exception as exc:
        # even though technically both of these could not have been
        # created with the exception having been thrown, we don't want
        # implementers to depend on the order of tagging / release
        # creation, so we insist that both untag_release and
        # destroy_release are safe as no-ops if the tag or release
        # doesn't exist, and call them both.
        #repo.untag_release(release_name, to_revision)
        #releases.destroy_release(release_name)
        return render_template('error.html', 
                               error_msg='Could not create the new release.',
                               error_detail=str(exc))

    return redirect(url_for('in_progress'))

@app.route('/delete_release', methods=['POST'])
def delete_release():
    g.releases.destroy_release(request.form['release_name'])
    return redirect(url_for('in_progress'))

@app.route('/release_detail/<release_name>/')
def release_detail(release_name):
    releases = g.releases
    
    release = releases.find_release(release_name)
    if not release:
        return render_template('release_not_found.html',
                               release_name=release_name), 404
    return render_template('release_detail.html',
                           release=release)

@app.route('/verify_commit', methods=['POST'])
def verify_commit():
    commit_id = request.form['commit_id']
    new_checked = request.form['checked']
    if new_checked == 'false':
        new_checked = False
    else:
        new_checked = True
    g.releases.verify_commit(commit_id, new_checked)
    return jsonify({'checked': new_checked})

if __name__ == '__main__':
    for config_module in sys.argv[1:]:
        app.config.from_object(config_module)
    app.run()
