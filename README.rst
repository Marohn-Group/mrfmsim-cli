mrfmsim-cli
======================

The *mrfmsim-cli* package is a part of the 
`mrfmsim project <https://marohn-group.github.io/mrfmsim-docs/>`__. 
The package provides quick command-line actions
for the *mrfmsim* packages, such as view the experiment and experiment group
metadata, vistualization and experiment execution.

.. note::
    The command line tool provides an easy way to quickly access and run
    *existing* experiments. For development, it is recommended to use the
    jupyter notebook environment.

To see the commands and options::

    mrfmsim --help


Commands
^^^^^^^^^^^^^^^
For detailed options, use ``mrfmsim command --help``.

The available commands for experiments:

- ``run``: execute the job (job defined using ``--job job_file`` option)
- ``visualize``: view the experiment model graph
- ``metadata``: show the experiment model metadata

Examples
^^^^^^^^^^^^^^^

To view the metadata of an experiment from ``mrfmsim.experiment``::

    mrfmsim metadata --expt IBMCyclic
    mrfmsim metadata --group CermitESRGroup --expt CermitESR

To view the metadata of an experiment from a custom module::

    mrfmsim metadata --module my_module --expt my_experiment

To visualize the experiment model graph::

    mrfmsim visualize --expt IBMCyclic

To run an experiment, the job file needs to be defined. It is recommended
to use the ``Job`` class to define the job file. In the file, a list of ``jobs``
needs to be supplied. An example of the job file:

.. code-block:: python

    # IBMCyclic_job.py
    from mrfmsim.job import Job
    from mrfmsim.shortcut import loop_shortcut

    job1 = Job(
        name="job1",
        inputs={
            "B0": ...,
            "df_fm": ...,
            "f_rf": ...,
            "grid": ...,
            "h": ...,
            "magnet": ...,
            "sample": ...,
        },
        shortcut=loop_shortcut(parameter="h"),
    )
    job2 = ...

    # a list named jobs needs to be defined
    jobs = [job1, job2]

To run the jobs

    mrfmsim run --expt IBMCyclic --job IBMCyclic_job.py
