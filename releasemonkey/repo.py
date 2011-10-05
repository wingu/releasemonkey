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
