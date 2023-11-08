from click.testing import CliRunner
from mrfmsim_cli.cli import cli
import pytest
import os
from textwrap import dedent
from unittest.mock import patch
import types
import mrfmsim.experiment as experiment_module
import mrfmsim as mrfmsim_module


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
    Usage: mrfmsim [OPTIONS] COMMAND [ARGS]...

      MRFM simulation tool

    Options:
      --help  Show this message and exit.

    Commands:
      metadata   show the experiment metadata
      plugins    list all available mrfmsim plugins
      run        run the job file, use '--job' for the job file path
      template   create a experiment template job file
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


def test_exp_missing_name_file_exception():
    """Test the load_experiment raise exception if the name and file are missing."""

    runner = CliRunner()
    result = runner.invoke(cli, ["metadata"])

    assert result.exit_code == 2
    assert "missing option '--name' or '--file'" in result.output


def test_file_missing_name_collection(collection_file):
    """Test exception if the file is a collection but no name."""

    runner = CliRunner()
    result = runner.invoke(cli, ["metadata", "-f", collection_file])

    assert result.exit_code == 2
    assert "collection missing option '--name'" in result.output


def test_invalid_file(tmp_path):
    """Test exception if the file is a collection but no name."""

    yaml_str = ""
    file_path = tmp_path / "test.yaml"
    file_path.write_text(yaml_str)

    runner = CliRunner()
    result = runner.invoke(cli, ["metadata", "-f", file_path])

    assert result.exit_code == 2
    assert "invalid experiment file" in result.output


def test_file_collection(collection_file):
    """Test obtain expt_collection."""

    runner = CliRunner()

    result = runner.invoke(cli, ["metadata", "-f", collection_file, "-n", "test1"])

    assert result.exit_code == 0
    assert "test1" in result.output


def test_collection(expt_collection):
    """Test obtain expt_collection."""

    runner = CliRunner()

    expt_module = types.ModuleType("mrfmsim.experiment")
    expt_module.test_collection = expt_collection

    with patch("mrfmsim_cli.cli.experiment_module", expt_module):
        result = runner.invoke(
            cli, ["metadata", "-c", "test_collection", "-n", "test1"]
        )

    assert result.exit_code == 0
    assert "test1" in result.output


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
        result = runner.invoke(cli, ["visualize", "-f", str(expt_file), "--no-view"])
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
    result = runner.invoke(cli, ["template", "-f", str(expt_file)])

    assert result.exit_code == 0
    assert result.output == dedent(job_template)


def test_cli_expt_execute(experiment_mod, job_file, mocker):
    """Test the experiment option works correctly.

    Here a mock module is created to create the test_experiment object.
    """

    runner = CliRunner()

    expt_module = types.ModuleType("mrfmsim.experiment")
    expt_module.test_experiment = experiment_mod

    with patch("mrfmsim_cli.cli.experiment_module", expt_module):
        result = runner.invoke(
            cli,
            ["run", "-n", "test_experiment", "--job", str(job_file)],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert (
        result.output.split("\n")[-2] == "[(0.0, 1.0), (-2.0, 1.0)]"
    )  # echo to console


def test_cli_expt_file_execute(expt_file, job_file):
    """Test the execute command executes the job correctly."""

    runner = CliRunner()
    result = runner.invoke(cli, ["run", "-f", str(expt_file), "--job", str(job_file)])

    assert result.exit_code == 0
    assert result.output.strip() == "[(0.0, 1.0), (-2.0, 1.0)]"  # echo to console


def test_cli_metadata(experiment_mod):
    """Test the metadata command has the correct output.

    Here a mock module is created to create the test_experiment object.
    """

    runner = CliRunner()

    # patch the experiment module so that the test does not depend on
    # the experiment plugins
    # here the key is to patch the module in the cli script

    expt_module = types.ModuleType("mrfmsim.experiment")
    expt_module.test_experiment = experiment_mod

    with patch("mrfmsim_cli.cli.experiment_module", expt_module):
        result = runner.invoke(cli, ["metadata", "-n", "test_experiment"])

    assert result.exit_code == 0
    assert str(experiment_mod) in result.output


def test_cli_show_plugin():
    """Test the show-plugin command."""

    runner = CliRunner()
    result = runner.invoke(cli, ["plugins"], catch_exceptions=False)

    assert result.exit_code == 0
