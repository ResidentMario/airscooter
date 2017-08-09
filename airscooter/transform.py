from pathlib import Path


class Transform:
    """A Transform is a data manipulation task that "transforms" input data into output data."""
    def __init__(self, name, filename, input, output, requirements=None, dummy=False):
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
        dummy: bool, default False
            Whether or not the op is a dummy operator (no-op). A dummy operator will be executed as a `DummyOperator`
            by airflow at runtime. This parameter is used for dealing with potentially long-running processes that
            you might want to trigger externally.
        """
        self.name = name
        self.filename = str(Path(filename).resolve(strict=False))
        self.input = [str(Path(inp).resolve(strict=False)) for inp in input]
        self.output = [str(Path(out).resolve(strict=False)) for out in output]
        self.requirements = [] if requirements is None else requirements
        self.dummy = dummy

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
                'type': 'transform',
                'dummy': self.dummy}

    def as_airflow_string(self):
        """
        Returns
        -------
        Returns this object's Airflow string, ready to be written to a Python DAG file. This method is used at the
        orchestration layer for instantiating the Airflow DAG. However, it is incomplete, because it does not set
        any task dependencies, which are handled separately in orchestration.
        """
        op_type = self.filename.rsplit(".")[-1]
        # op_id = ".".join(self.filename.rsplit(".")[:-1]).split("/")[-1]
        # print("\n\n{0}\n\n".format(self.filename))
        # print("\n\n{0}\n\n".format(op_type))

        if self.dummy:
            return """DummyOperator(task_id="{0}", dag=dag)""".format(
                ".".join(self.filename.rsplit(".")[:-1]).split("/")[-1]
            )
        elif op_type == "sh":
            with open(self.filename, 'r') as f:
                bash_command = f.read()

            return """BashOperator(bash_command=\"\"\"{0} \"\"\", task_id="{1}", dag=dag)""".format(
                bash_command, self.name
            )
        elif op_type == "py":
            # Airflow provides a Python operator for executing callable Python code objects. However, this is not
            # particularly desirable in terms of security because that would mean invoking an exec. A bash operator
            # launching the script as a process is safer.
            return """BashOperator(bash_command="python {0}", task_id="{1}", dag=dag)""".format(
                self.filename, self.name
            )
        elif op_type == "ipynb":
            return """BashOperator(bash_command="jupyter nbconvert --to notebook""" + \
                   """ --execute {0}", task_id="{1}", dag=dag)""".format(
                       self.filename, self.name
            )
        else:
            raise NotImplementedError("The given operation type was not understood.")
