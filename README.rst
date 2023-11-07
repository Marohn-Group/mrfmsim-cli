mrfmsim-cli
======================

``mrfmsim-cli`` provides quick command line actions for the mrfmsim packaegs.


To see the commands and options::

    mrfmsim --help

To list all available plugins::

    mrfmsim plugins

Specifically, the interface takes two stages, first to load the experiment,
and then execute related commands.

Load Experiment
^^^^^^^^^^^^^^^

The experiments can be loaded in two ways:

- Load experiments from 'experiment' plugin using ``--expt expt_to_load``.
- Load experiments from YAML file using ``--expt-file exp_file_path``.


Execute Command
^^^^^^^^^^^^^^^
The other command other than 'plugins' should follow after loading the experiment::

    mrfmsim --exp exp_to_load command

The available commands are:

- ``execute``: execute the job (job defined using ``--job job_file`` option)
- ``visualize``: draw the experiment model graph
- ``metadata``: show the experiment model metadata
- ``template``: create a template job file based on the experiment
