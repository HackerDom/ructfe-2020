
class Storage(object):
    def write(self, key, value):
        with open(u"storage/{}".format(key), mode=u"w") as f:
            f.write(value.strip())

    def read(self, key):
        with open(u"storage/{}".format(key)) as f:
            return f.read().strip()