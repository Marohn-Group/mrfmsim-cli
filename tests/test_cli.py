from click.testing import CliRunner
from mrfmsim_cli.cli import cli
import os
from textwrap import dedent
import types
import sys


def test_cli_help():
    """Test the help command executes the job correctly."""

    help_str = """\
    Usage: mrfmsim [OPTIONS] COMMAND [ARGS]...

      MRFM simulation tool

    Options:
      --help  Show this message and exit.

    Commands:
      metadata   show the experiment metadata
      run        run the job file, use '--job' for the job file path
      visualize  view the experiment graph
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert result.output == dedent(help_str)


def test_cli_help_command():
    """Test the command line outputs the help function if no command is given."""

    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    assert "Usage: mrfmsim [OPTIONS] COMMAND [ARGS]..." in result.output


def test_exp_missing_name_exception():
    """Test the load_experiment raise exception if the name and file are missing."""

    runner = CliRunner()
    result = runner.invoke(cli, ["metadata"])

    assert result.exit_code == 2
    assert "experiment or experiment group not defined" in result.output


def test_experiment_group(experiment_group):
    """Test obtain experiment_group."""

    runner = CliRunner()

    expt_module = types.ModuleType("mock_module")
    sys.modules["mock_module"] = expt_module
    expt_module.test_collection = experiment_group

    result = runner.invoke(
        cli, ["metadata", "-m", "mock_module", "-g", "test_collection", "-e", "recipe1"]
    )

    assert result.exit_code == 0
    assert "recipe1" in result.output


def test_experiment_group_metadata(experiment_group):
    """Test experiment_group can display metadata without specify experiment name."""

    runner = CliRunner()

    expt_module = types.ModuleType("mock_module")
    sys.modules["mock_module"] = expt_module
    expt_module.test_collection = experiment_group

    result = runner.invoke(
        cli, ["metadata", "-m", "mock_module", "-g", "test_collection"]
    )

    assert result.exit_code == 0
    assert "experiments: ['recipe1', 'recipe2']" in result.output


def test_cli_visualize(experiment_mod):
    """Test the visualize command outputs the correct dot file.

    The render to the browser is turned off.
    """

    dot_source = """digraph test_graph {
    graph [label="test_experiment(comp, d_loop, f, h=2)
    returns: (k, m)
    return_units: {'k': 'm^2'}
    graph: test_graph
    handler: MemHandler
    modifiers:
    - loop_input(parameter='d')
    Test experiment with components." 
    labeljust=l labelloc=t ordering=out splines=ortho]
    node [shape=box]
    add [label="add
    add(a, h)
    return: c
    functype: numpy.ufunc
    Add a and h."]
    subtract [label="subtract
    sub(c, d)
    return: e
    functype: builtin_function_or_method
    Same as a - b."]
    power [label="power
    pow(c, f)
    return: g
    functype: builtin_function_or_method
    Return x**y (x to the power of y)."]
    log [label="log
    log(c, b)
    return: m
    functype: builtin_function_or_method
    Return the logarithm of x to the given base."]
    multiply [label="multiply
    multiply(e, g)
    return: k
    functype: numpy.ufunc
    Multiply arguments element-wise."]
    add -> subtract [xlabel="c"]
    add -> power [xlabel="c"]
    add -> log [xlabel="c"]
    subtract -> multiply [xlabel="e"]
    power -> multiply [xlabel="g"]
    }"""

    runner = CliRunner()
    with runner.isolated_filesystem():

        expt_module = types.ModuleType("mock_module")
        sys.modules["mock_module"] = expt_module
        expt_module.test_experiment = experiment_mod

        result = runner.invoke(
            cli,
            ["visualize", "-m", "mock_module", "-e", "test_experiment", "--no-view"],
        )
        assert result.exit_code == 0
        assert result.output == ""  # output to the console

        # The name of the file is the name of the graph.
        with open("test_graph.gv", "r") as f:
            dot_graph = f.read()
            dot_graph_source = (
                dot_graph.replace("\t", "").replace(r"\l", "\n").replace("\n", "")
            )
        assert dot_graph_source == dedent(dot_source).replace("\n", "").replace(
            "    ", ""
        )
        assert os.path.exists("test_graph.gv.pdf")


def test_cli_exception(experiment_group):
    """Test the visualize exception when only the group is given."""

    runner = CliRunner()

    expt_module = types.ModuleType("mock_module")
    sys.modules["mock_module"] = expt_module
    expt_module.test_collection = experiment_group

    result = runner.invoke(
        cli, ["visualize", "-m", "mock_module", "-g", "test_collection"]
    )
    assert result.exit_code == 2
    assert "experiment not defined" in result.output

    result = runner.invoke(cli, ["run", "-m", "mock_module", "-g", "test_collection"])
    assert result.exit_code == 2
    assert "experiment not defined" in result.output


def test_cli_expt_run(experiment_mod, job_file):
    """Test the experiment option works correctly.

    Here a mock module is created to create the test_experiment object.
    """

    runner = CliRunner()

    expt_module = types.ModuleType("mock_module")
    sys.modules["mock_module"] = expt_module
    expt_module.test_experiment = experiment_mod

    result = runner.invoke(
        cli,
        [
            "run",
            "-m",
            "mock_module",
            "-e",
            "test_experiment",
            "--job",
            str(job_file),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert (
        result.output.split("\n")[-2]
        == "[(np.float64(0.0), 1.0), (np.float64(-2.0), 1.0)]"
    )  # echo to console
