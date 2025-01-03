import click
from mrfmsim_cli.job import job_execution
from functools import wraps
import importlib


def load_experiment(command_func):
    """Load experiment or experiment group."""

    @click.option("--expt", "-e", type=str, help="load an experiment")
    @click.option("--group", "-g", type=str, help="load a experiment group")
    @click.option(
        "--module",
        "-m",
        type=str,
        help="experiment module, defaults to mrfmsim.experiment",
    )
    @wraps(command_func)
    def wrapper(expt, group, module, **kwargs):

        if not expt and not group:
            raise click.UsageError("experiment or experiment group not defined")
        module = module or "mrfmsim.experiment"
        expt_module = importlib.import_module(module)

        if group:
            experiment_group = getattr(expt_module, group)
            if expt:
                experiment = experiment_group.experiments[expt]
            else:
                experiment = None

        else:
            experiment = getattr(expt_module, expt)
            experiment_group = None

        return command_func(
            experiment=experiment, experiment_group=experiment_group, **kwargs
        )

    return wrapper


@click.group(help="MRFM simulation tool", name="mrfmsim")
def cli():
    """Main function for the CLI."""
    pass


@cli.command(help="view the experiment graph")
@load_experiment
@click.option("--view/--no-view", is_flag=True, default=True)
def visualize(experiment, experiment_group, view):
    """Draw experiment graph."""
    if not experiment:
        raise click.UsageError("experiment not defined")
    dot_graph = experiment.visualize()
    dot_graph.render(view=view)


@cli.command(help="show the experiment metadata")
@load_experiment
def metadata(experiment, experiment_group):
    """Show experiment metadata."""

    if experiment:
        click.echo(str(experiment))
    else:
        click.echo(str(experiment_group))

@cli.command(help="run the job file, use '--job' for the job file path")
@load_experiment
@click.option("--job", "-j", help="the job file path")
def run(experiment, experiment_group, job):
    """Execute the job file, use --job for the job file path."""
    if not experiment:
        raise click.UsageError("experiment not defined")
    spec = importlib.util.spec_from_file_location("job_file", job)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    jobs = module.jobs

    for j in jobs:
        # return the result to the console
        click.echo(job_execution(experiment, j))
