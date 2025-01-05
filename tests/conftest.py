import pytest
import math
from mmodel.modifier import loop_input
from mrfmsim import Experiment, Graph, Node, ExperimentGroup
from textwrap import dedent
import numpy as np
import operator


@pytest.fixture
def node_edges():
    """Node objects and grouped edges for creating a graph."""

    grouped_edges = [
        ("add", ["subtract", "power", "log"]),
        (["subtract", "power"], "multiply"),
    ]

    node_objects = [
        Node("add", np.add, inputs=["a", "h"], output="c", doc="Add a and h."),
        Node("subtract", operator.sub, inputs=["c", "d"], output="e"),
        Node("power", math.pow, inputs=["c", "f"], output="g"),
        Node("multiply", np.multiply, inputs=["e", "g"], output="k", output_unit="m^2"),
        Node("log", math.log, inputs=["c", "b"], output="m"),
    ]

    return grouped_edges, node_objects


@pytest.fixture
def modelgraph(node_edges):
    """Model graph for creating experiment and model.

    The results are:
    k = (a + h - d)(a + h)^f
    m = log(a + h, b)

    h defaults to 2
    """

    grouped_edges, node_objects = node_edges

    G = Graph(name="test_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)

    return G


@pytest.fixture
def experiment(modelgraph):
    """Test experiment instance with default settings."""
    return Experiment("test_experiment_plain", modelgraph, param_defaults={"h": 2})


@pytest.fixture
def experiment_mod(modelgraph):
    """Test experiment instance with modifiers and component substitutions."""

    return Experiment(
        "test_experiment",
        modelgraph,
        components={"comp": ["a", "b"]},
        modifiers=[loop_input(parameter="d")],
        doc="Test experiment with components.",
        param_defaults={"h": 2},
    )


@pytest.fixture
def experiment_group(experiment_mod):
    """Test experiment group."""
    return {"test1": experiment_mod, "test2": experiment_mod}


@pytest.fixture
def experiment_group(node_edges):
    """Test experiment instance with groupings."""

    grouped_edges, node_objects = node_edges

    experiment_recipes = {
        "recipe1": {
            "grouped_edges": grouped_edges,
            "param_defaults": {"h": 2},
        },
        "recipe2": {
            "grouped_edges": grouped_edges,
            "param_defaults": {"h": 3},
        },
    }

    return ExperimentGroup(
        "test_experiment_group",
        node_objects,
        experiment_recipes,
        doc="Test experiment group with multiple recipes.",
    )


@pytest.fixture
def job_file(tmp_path):
    """Create a custom job file."""

    job_content = """

    from mrfmsim_cli.job import Job
    from types import SimpleNamespace

    comp = SimpleNamespace(a=0, b=2)
    job1 = Job(name="job1", inputs={'comp':comp, 'd_loop':[2, 3], 'f':1, 'h':2})

    jobs = [job1]
    """

    f_path = tmp_path / "job.py"
    f_path.write_text(dedent(job_content))
    return f_path
