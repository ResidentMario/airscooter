class Transform:
    """A Transform is a data manipulation task that "transforms" input data into output data."""
    def __init__(self, name, filename, input, output, requirements=None):
        """
        Parameters
        ----------
        name, str, required
            The name of the transform. This corresponds with the airflow task_id. A task name is required,
            and the name must be unique to this particular task.
        filename: str, required
            The name of the file that will executed at runtime to implement this transform. A determination on *how*
            this file will be run is made at processing time using the file's extension. If no extension is provided in
            the filename, or the extension is not in the list of extensions handled, an exception will be raised.

            Note that in general, most any process imaginable can be piped through a shell script (a `.sh` file). If
            you are using code with an extension not in the list, wrapping it in a shell script is a simple way of
            handling the issue.
        input: str, required
            The filename of the file that is being used as an input to this task. At the CLI level, the input is used
            to generate this transform's (singular) list of requirements. However, at the object level, the input and
            requirements are divorced from one another, parameter-wise.

            This is because it is algorithmically easier to handle linking in requirements if we can do so later than
            at instantiation time.
        output: str, required
            The filename of the file that is being generated as output to this task. This parameter is used at the
            CLI level to determine prerequisites for possible further transforms dependent on this one.
        requirements: list of {Transform, Depositor} objects, optional
            A list of requirements for this task. At the moment, multiple requirements are possible, but this may
            change in the future. Defaults to an empty list (`[]`).
        """
        self.name = name
        self.filename = filename
        self.input = input
        self.output = output
        self.requirements = [] if requirements is None else requirements

    def datafy(self):
        """
        Returns
        -------
        Returns this object's simplified JSON representation. This is used for serialization to YAML, which is used
        in turn to allow object persistence.
        """
        return {'name': self.name,
                'filename': self.filename,
                'input': self.input,
                'output': self.output,
                'requirements': [r.name for r in self.requirements],
                'type': 'transform'}

    def as_airflow_string(self):
        """
        Returns
        -------
        Returns this object's Airflow string, ready to be written to a Python DAG file. This method is used at the
        orchestration layer for instantiating the Airflow DAG. However, it is incomplete, because it does not set
        any task dependencies, which are handled separately in orchestration.
        """
        op_type = self.filename.rsplit(".")[-1]
        if op_type == "sh":
            return """BashOperator(bash_command="{0} ", task_id="{1}", dag=dag)
    """.format(self.filename, ".".join(self.filename.rsplit(".")[:-1]).split("/")[-1])

    # def run2(self):
    #     nb = nbformat.read(self.notebook, nbformat.current_nbformat)
    #     # https://nbconvert.readthedocs.io/en/latest/execute_api.html
    #     ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, kernel_name='python3')
    #     try:
    #         ep.preprocess(nb, {'metadata': {'path': "/".join(self.notebook.split("/")[:-1])}})
    #         with self.output().open('w') as f:
    #             nbformat.write(nb, f)
    #     except CellExecutionError:
    #         pass
