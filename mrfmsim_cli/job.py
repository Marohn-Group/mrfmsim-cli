class Job:
    """Create Experiment execution job.

    :param str name: name of the job
    :param dict inputs: input needed for model
    :param list shortcuts: additional shortcut modification of the model
    """

    def __init__(self, name, inputs, shortcuts=None):
        self.name = name
        self.shortcuts = shortcuts or []
        self.inputs = inputs


def job_execution(experiment, job: Job):
    """Execute experiment based on the job."""

    for shortcut, kwargs in job.shortcuts:
        experiment = shortcut(experiment, **kwargs)

    return experiment(**job.inputs)
