class KeyDefaultDict(dict):
    def __init__(self, factory, meta=None):
        self.factory = factory
        self.meta = meta

    def __missing__(self, key):
        if self.meta is not None:
            self[key] = self.factory(key, self.meta)
        else:
            self[key] = self.factory(key)

        return self[key]
