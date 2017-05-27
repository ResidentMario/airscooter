class Action:

    def __init__(self, cell):
        self.source = cell['source']

        out = cell['outputs']
        self.ran = len(out) != 0
        self.success = self.ran and not any(map(lambda o: 'ename' in o.keys(), out))
