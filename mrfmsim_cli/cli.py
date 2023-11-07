import click
from mrfmsim.configuration import MrfmSimLoader
from mrfmsim_cli.job import Job, job_execution
from mrfmsim_cli.configuration import TemplateDumper
from mrfmsim import Experiment, PLUGINS
import importlib
import yaml
import sys


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--expt-file",
    type=click.Path(exists=True),
    default=None,
    help="Load experiment by file path.",
)
@click.option("--expt", type=str, default=None, help="Load experiment by name.")
def cli(ctx, expt_file, expt):
    """MRFM simulation tool."""

    if ctx.invoked_subcommand is None:
        if any([expt_file, expt]):
            raise click.UsageError("No commands are given.")
        click.echo(ctx.get_help())
    else:
        ctx.ensure_object(dict)
        if expt_file and expt:
            raise click.BadOptionUsage(
                "expt-file", "cannot use both 'expt-file' and 'expt' options"
            )
        elif expt_file:
            with open(expt_file, "r") as f:
                experiment = yaml.load(f, Loader=MrfmSimLoader)
            ctx.obj["experiment"] = experiment
        elif expt:
            experiment_module = sys.modules["mrfmsim.experiment"]
            ctx.obj["experiment"] = getattr(experiment_module, expt)


@cli.command()
@click.pass_context
@click.option("--view/--no-view", is_flag=True, default=True)
def visualize(ctx, view):
    """Draw experiment graph."""
    dot_graph = ctx.obj["experiment"].visualize()
    dot_graph.render(view=view)


@cli.command()
@click.pass_context
def metadata(ctx):
    """Show experiment metadata."""
    expt_obj = str(ctx.obj["experiment"])
    click.echo(expt_obj)


@cli.command()
@click.pass_context
def template(ctx):
    """Create a template job file based on the experiment."""
    experiment = ctx.obj["experiment"]
    job_template = [Job("", {k: None for k in experiment.__signature__.parameters}, [])]
    click.echo(yaml.dump(job_template, Dumper=TemplateDumper, sort_keys=False))


@cli.command()
@click.pass_context
@click.option("--job", help="The job file path.")
def execute(ctx, job):
    """Execute the job file, use --job for the job file path."""
    experiment = ctx.obj["experiment"]

    with open(job, "r") as f:
        jobs = yaml.load(f, Loader=MrfmSimLoader)

    for job in jobs:
        # return the result to the console
        click.echo(job_execution(experiment, job))


@cli.command()
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
