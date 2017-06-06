import luigi


class Runner(luigi.Task):
    """Stub class that runs a set of tasks. May be invoked programmatically using run()."""
    requirements = luigi.ListParameter()

    def requires(self):
        return self.requirements
