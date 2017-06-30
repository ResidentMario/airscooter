class Depositor:
    """Foo."""
    def __init__(self, filename, output, dummy=False):
        self.filename = filename
        self.output = output
        self.dummy = dummy

    def opify(self):
        """
        Returns the requisite Airflow operator for performing the targeted operation.
        """
        op_type = self.filename.split(".")[1][1:]
        if op_type == "sh":
            # noinspection PyUnresolvedReferences
            return operators.BashOperator(self.filename)
        else:
            # TODO
            pass
