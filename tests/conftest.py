import pytest
import math
from mmodel.modifier import loop_input
from mrfmsim import Experiment, Graph, Node
from textwrap import dedent
import numpy as np
import operator


@pytest.fixture
def modelgraph():
    """Model graph for creating experiment and model.

    The results are:
    k = (a + h - d)(a + h)^f
    m = log(a + h, b)

    h defaults to 2
    """

    grouped_edges = [
        ("add", ["subtract", "power", "log"]),
        (["subtract", "power"], "multiply"),
    ]

    node_objects = [
        Node("add", np.add, inputs=["a", "h"], output="c"),
        Node("subtract", operator.sub, inputs=["c", "d"], output="e"),
        Node("power", math.pow, inputs=["c", "f"], output="g"),
        Node("multiply", np.multiply, inputs=["e", "g"], output="k", output_unit="m^2"),
        Node("log", math.log, inputs=["c", "b"], output="m"),
    ]

    G = Graph(name="test_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)

    return G


@pytest.fixture
def experiment(modelgraph):
    """Test experiment instance with default settings."""
    return Experiment("test_experiment_plain", modelgraph, defaults={"h": 2})


@pytest.fixture
def experiment_mod(modelgraph):
    """Test experiment instance with modifiers and component substitutions."""

    return Experiment(
        "test_experiment",
        modelgraph,
        components={"comp": [("a", "a1"), ("b", "b1")]},
        modifiers=[loop_input(parameter="d")],
        doc="Test experiment with components.",
        defaults={"h": 2},
    )


@pytest.fixture
def expt_file(tmp_path):
    """Create a custom module for testing."""

    expt_yaml = """\
    !Experiment
    name: test_experiment
    graph:
        !Graph
        name: test_graph
        grouped_edges:
            - [add, [subtract, power, log]]
            - [[subtract, power], multiply]
        node_objects:
            add:
                func: !func:add "lambda a, h: a + h"
                doc: Add a and h.
                inputs: [a, h]
                output: c
            subtract:
                func: !import operator.sub
                output: e
                inputs: [c, d]
            power:
                func: !import math.pow
                output: g
                inputs: [c, f]
            multiply:
                func: !import numpy.multiply
                output: k
                inputs: [e, g]
                output_unit: m^2
            log:
                func: !import math.log
                output: m
                inputs: [c, b]
    components: {comp: [[a, a1], [b, b1]]}
    doc: Test experiment with components.
    modifiers: [!import:mmodel.modifier.loop_input {parameter: d}]
    defaults:
        h: 2
    """

    expt_yaml = dedent(expt_yaml)

    module_path = tmp_path / "expt.yaml"
    module_path.write_text(expt_yaml)
    return module_path
