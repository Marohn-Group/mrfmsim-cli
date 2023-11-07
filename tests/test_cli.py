from click.testing import CliRunner
from mrfmsim_cli.cli import cli
import pytest
import os
from textwrap import dedent
from unittest.mock import patch
import types


@pytest.fixture
def job_file(tmp_path):
    """Create a job yaml file."""

    job_yaml = """\
    - !import:mrfmsim_cli.job.Job
      name: test
      inputs:
        comp:
          !import:types.SimpleNamespace
          a1: 0
          b1: 2
        d_loop: [2, 3]
        f: 1
        h: 2
      shortcuts: []
    """

    module_path = tmp_path / "job.yaml"
    module_path.write_text(dedent(job_yaml))
    return module_path


def test_cli_help():
    """Test the help command executes the job correctly."""

    help_str = """\
    Usage: cli [OPTIONS] COMMAND [ARGS]...

      MRFM simulation tool.

    Options:
      --expt-file PATH  Load experiment by file path.
      --expt TEXT       Load experiment by name.
      --help            Show this message and exit.

    Commands:
      execute    Execute the job file, use --job for the job file path.
      metadata   Show experiment metadata.
      plugins    List all available plugins.
      template   Create a template job file based on the experiment.
      visualize  Draw experiment graph.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert dedent(help_str) == result.output


def test_cli_help_command():
    """Test the command line outputs the help function if no command is given."""

    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output


def test_cli_option_raises_error(expt_file):
    """Test the command line raises an error if both exp-file and exp are given."""

    runner = CliRunner()
    result = runner.invoke(
        cli, ["--expt-file", str(expt_file), "--expt", "test", "metadata"]
    )

    assert result.exit_code == 2
    assert "cannot use both 'expt-file' and 'expt' options" in result.output


def test_cli_no_command_error(expt_file):
    """Test the command line raises an error if no command is given."""

    runner = CliRunner()
    result = runner.invoke(cli, ["--expt-file", str(expt_file)])

    assert result.exit_code == 2
    assert "No commands are given." in result.output



def test_cli_visualize(expt_file):
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
    - loop_input('d')
    components:
    - comp: [['a', 'a1'], ['b', 'b1']]
    Test experiment with components." 
    labeljust=l labelloc=t ordering=out splines=ortho]
    node [shape=box]
    add [label="add
    add(a, h)
    return: c
    functype: function
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
        result = runner.invoke(
            cli, ["--expt-file", str(expt_file), "visualize", "--no-view"]
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


def test_cli_template(expt_file):
    """Test the template command outputs the value correctly."""

    job_template = """\
    - !import:mrfmsim.Job
      name: ''
      inputs:
        comp: null
        d_loop: null
        f: null
        h: null
      shortcuts: []

    """

    runner = CliRunner()
    result = runner.invoke(cli, ["--expt-file", str(expt_file), "template"])

    assert result.exit_code == 0
    assert result.output == dedent(job_template)


def test_cli_expt_execute(experiment_mod, job_file):
    """Test the experiment option works correctly.

    Here a mock module is created to create the test_experiment object.
    """

    runner = CliRunner()

    child_module = types.ModuleType("mrfmsim.experiment")
    child_module.test_experiment = experiment_mod

    with patch.dict("sys.modules", {"mrfmsim.experiment": child_module}):
        result = runner.invoke(
            cli,
            ["--expt", "test_experiment", "execute", "--job", str(job_file)],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert (
        result.output.split("\n")[-2] == "[(0.0, 1.0), (-2.0, 1.0)]"
    )  # echo to console


def test_cli_expt_file_execute(expt_file, job_file):
    """Test the execute command executes the job correctly."""

    runner = CliRunner()
    result = runner.invoke(
        cli, ["--expt-file", str(expt_file), "execute", "--job", str(job_file)]
    )

    assert result.exit_code == 0
    assert result.output.strip() == "[(0.0, 1.0), (-2.0, 1.0)]"  # echo to console


def test_cli_metadata(experiment_mod):
    """Test the metadata command has the correct output.

    Here a mock module is created to create the test_experiment object.
    """

    runner = CliRunner()

    child_module = types.ModuleType("mrfmsim.experiment")
    child_module.test_experiment = experiment_mod

    with patch.dict("sys.modules", {"mrfmsim.experiment": child_module}):
        result = runner.invoke(cli, ["--expt", "test_experiment", "metadata"])

    assert result.exit_code == 0
    assert str(experiment_mod) in result.output



def test_cli_show_plugin():
    """Test the show-plugin command."""

    runner = CliRunner()
    result = runner.invoke(cli, ["plugins"], catch_exceptions=False)

    assert result.exit_code == 0
