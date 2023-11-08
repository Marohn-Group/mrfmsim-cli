import click
from mrfmsim.configuration import MrfmSimLoader
from mrfmsim_cli.job import Job, job_execution
from mrfmsim_cli.configuration import TemplateDumper
from mrfmsim import Experiment, ExperimentCollection, PLUGINS
import mrfmsim.experiment as experiment_module
import yaml
from functools import wraps


def load_experiment(command_func):
    """Load experiment from file or collection as a common option decorator."""

    @click.option("--name", "-n", type=str, help="experiment name")
    @click.option(
        "--file",
        "-f",
        type=click.Path(exists=True),
        help="load experiment/collection by file path",
    )
    @click.option("--collection", "-c", type=str, help="load experiment collection")
    @wraps(command_func)
    def wrapper(name, file, collection, **kwargs):
        if not any([name, file]):
            raise click.UsageError("missing option '--name' or '--file'")

        if file:
            with open(file, "r") as f:
                obj = yaml.load(f, Loader=MrfmSimLoader)
            if isinstance(obj, Experiment):
                experiment = obj
            elif isinstance(obj, ExperimentCollection):
                if not name:
                    raise click.UsageError("collection missing option '--name'")
                experiment = obj[name]
            else:
                raise click.UsageError("invalid experiment file")
        elif collection:
            experiment = getattr(experiment_module, collection)[name]
        else:
            experiment = getattr(experiment_module, name)

        return command_func(experiment=experiment, **kwargs)

    return wrapper


@click.group(help="MRFM simulation tool", name="mrfmsim")
def cli():
    """Main function for the CLI."""
    pass


@cli.command(help="view the experiment graph")
@load_experiment
@click.option("--view/--no-view", is_flag=True, default=True)
def visualize(experiment, view):
    """Draw experiment graph."""
    dot_graph = experiment.visualize()
    dot_graph.render(view=view)


@cli.command(help="show the experiment metadata")
@load_experiment
def metadata(experiment):
    """Show experiment metadata."""
    click.echo(str(experiment))


@cli.command(help="create a experiment template job file")
@load_experiment
def template(experiment):
    """Create a template job file based on the experiment."""
    job_template = [Job("", {k: None for k in experiment.__signature__.parameters}, [])]
    click.echo(yaml.dump(job_template, Dumper=TemplateDumper, sort_keys=False))


@cli.command(help="run the job file, use '--job' for the job file path")
@load_experiment
@click.option("--job", help="the job file path")
def run(experiment, job):
    """Execute the job file, use --job for the job file path."""

    with open(job, "r") as f:
        jobs = yaml.load(f, Loader=MrfmSimLoader)

    for j in jobs:
        # return the result to the console
        click.echo(job_execution(experiment, j))


@cli.command(help="list all available mrfmsim plugins")
def plugins():
    """List all available plugins."""

    for plugin, eps in PLUGINS.items():
        click.echo(plugin)
        for ep_dict in eps:
            for key, val in ep_dict.items():
                if key == "module":
                    click.echo(f"\t{key}: {val.__name__}")
                else:
                    click.echo(f"\t{key}: {val}")
