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
        self.filename = filename
        self.output = output

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
        op_type = self.filename.split(".")[1]
        if op_type == "sh":
            return """BashOperator(bash_command="{0}", task_id="{1}", dag=dag)
""".format(self.filename, self.filename.split(".")[0])
