from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy import ForeignKey

# TODO this should take from a config file.
engine = create_engine('sqlite:///test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Commit(Base):
    __tablename__ = 'commits'
    id = Column(Integer(), primary_key=True)
    revision = Column(Text())
    is_verified = Column(Boolean())
    release_id = Column(Integer(), ForeignKey('releases.id'))
    release = relationship('Release', 
                           backref=backref('commits', order_by=revision))
    author = Column(Text())
    msg = Column(Text())
    link = Column(Text())

    MAX_SNIPPET_LEN = 255

    def __init__(self, release_id, revision, author, msg, link):
        self.release_id = release_id
        self.revision = revision
        self.author = author
        self.msg = msg
        self.link = link
        self.is_verified = False

    def msg_snippet(self):
        if len(self.msg) > self.MAX_SNIPPET_LEN:
            return self.msg[:self.MAX_SNIPPET_LEN] + '...'
        else:
            return self.msg

class Release(Base):
    __tablename__ = 'releases'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), unique=True)
    from_revision = Column(Text())
    to_revision = Column(Text())
    in_progress = Column(Boolean())

    def __init__(self, name=None, from_revision=None, to_revision=None, in_progress=False):
        self.name = name
        self.from_revision = from_revision
        self.to_revision = to_revision
        self.in_progress = in_progress

    def __repr__(self):
        return '<Release %r>' % (self.name)

    def count_unverified_commits(self):
        return len([c for c in self.commits if not c.is_verified])

    def count_total_commits(self):
        return len(self.commits)


def init_db():
    Base.metadata.create_all(bind=engine)
    # TODO add a trigger to make sure only one release can be in progress

def remove_db_session():
    db_session.remove()

class SqliteReleases(object):

    def __init__(self, db_session):
        self.db_session = db_session

    def in_progress(self):
        return self.db_session.query(Release).filter_by(in_progress=True)

    def finished(self):
        return self.db_session.query(Release).filter_by(in_progress=False)

    def suggested_release_name(self):
        return "sqlite_suggested_release"

    def create_release(self, release_name, from_revision, to_revision, commits):
        rel = Release(release_name, from_revision, to_revision, True)
        self.db_session.add(rel)
        try:
            self.db_session.commit()
        except:
            self.db_session.rollback()
            raise
        for commit in commits:
            self.db_session.add(Commit(release_id=rel.id,
                                       revision=commit.revision,
                                       msg=commit.msg,
                                       author=commit.author,
                                       link=commit.link))
        try:
            self.db_session.commit()
        except:
            self.db_session.rollback()
            raise

    def destroy_release(self, release_name):
        release = self.db_session.query(Release).filter_by(name=release_name)
        if release:
            release.delete()
            try:
                self.db_session.commit()
            except:
                # TODO LOG
                self.db_session.rollback()
    
    def find_release(self, release_name):
        return self.db_session.query(Release).filter_by(name=release_name).first()

    def verify_commit(self, commit_id, verified):
        if verified:
            verified = 1
        else:
            verified = 0

        commit = self.db_session.query(Commit).filter_by(id=commit_id).one()
        commit.is_verified = verified

        try:
            self.db_session.commit()
        except:
            # TODO log
            self.db_session.rollback()

    def mark_release_finished(self, release_name):
        release = self.find_release(release_name)
        if not release:
            raise Exception("Couldn't find release %s" % release_name)
        unverified_count = release.count_unverified_commits()
        if unverified_count:
            err_msg = "Cannot mark release finished with %d unverified commits" % unverified_count
            raise Exception(err_msg)
        release.in_progress = False
        try:
            self.db_session.commit()
        except:
            self.db_session.rollback()
            raise

    def mark_release_in_progress(self, release_name):
        release = self.find_release(release_name)
        if not release:
            raise Exception("Couldn't find release %s" % release_name)
        release.in_progress = True
        try:
            self.db_session.commit()
        except:
            self.db_session.rollback()
            raise


            
RELEASES = SqliteReleases(db_session)
TEARDOWNS = [remove_db_session]
