from pathlib import Path


class Depositor:
    """
    A Depositor is (ontologically) a data dumping task that takes data from somewhere and places it onto the local
    machine.
    """
    def __init__(self, name, filename, output):
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
        output: str, required
            The filename of the file that is being generated as output to this task. This parameter is used at the
            CLI level to determine prerequisites for possible further transforms dependent on this one.
        """
        self.name = name
        self.filename = str(Path(filename).resolve())
        self.output = [str(Path(out).resolve()) for out in output]

    def datafy(self):
        """
        Returns
        -------
        Returns this object's simplified JSON representation. This is used for serialization to YAML, which is used
        in turn to allow object persistence.
        """
        return {'name': self.name,
                'filename': self.filename,
                'output': self.output,
                'type': 'depositor'}

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
        print("\n\n{0}\n\n".format(self.filename))
        print("\n\n{0}\n\n".format(op_type))

        if op_type == "sh":
            with open(self.filename, 'r') as f:
                bash_command = f.read()

            return """BashOperator(bash_command=\"\"\"{0} \"\"\", task_id="{1}", dag=dag)""".format(
                bash_command, ".".join(self.filename.rsplit(".")[:-1]).split("/")[-1]
            )
        elif op_type == "py":
            # Airflow provides a Python operator for executing callable Python code objects. However, this is not
            # particularly desirable in terms of security because that would mean invoking an exec. A bash operator
            # launching the script as a process is safer.
            return """BashOperator(bash_command="python {0}", task_id="{1}", dag=dag)""".format(
                self.filename, ".".join(self.filename.rsplit(".")[:-1]).split("/")[-1]
            )
        elif op_type == "ipynb":
            pass
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
        else:
            raise NotImplementedError("The given operation type was not understood.")
