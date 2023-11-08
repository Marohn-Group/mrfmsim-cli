import yaml
from mrfmsim_cli.job import Job


def yaml_dumper(representer_dict):
    """Create a yaml dumper with custom representers.

    :param dict representer_dict: dictionary of representer
    :returns: yaml dumper class
    """

    class Dumper(yaml.SafeDumper):
        pass

    for key, value in representer_dict.items():
        Dumper.add_representer(key, value)

    return Dumper


def job_representer(dumper: yaml.SafeDumper, job: Job):
    """Represent a Job instance."""

    return dumper.represent_mapping(
        "!import:mrfmsim.Job",
        {"name": job.name, "inputs": job.inputs, "shortcuts": job.shortcuts},
    )


default_representers = {
    Job: job_representer,
}

TemplateDumper = yaml_dumper(default_representers)
