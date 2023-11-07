from mrfmsim_cli.job import Job, job_execution
from mrfmsim.shortcut import loop_shortcut


def test_job_execution(experiment):
    """Test the job execution."""

    job = Job(
        "test",
        {"a_loop": [0, 2], "b": 2, "d": 1, "f": 3},
        [(loop_shortcut, {"parameter": "a"})],
    )

    assert job_execution(experiment, job) == [(8, 1), (192, 2)]
