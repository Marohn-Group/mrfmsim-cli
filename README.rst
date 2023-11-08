mrfmsim-cli
======================

``mrfmsim-cli`` provides quick command line actions for the mrfmsim packaegs.


To see the commands and options::

    mrfmsim --help

To list all available plugins::

    mrfmsim plugins

Specifically, the interface takes two stages, first to load the experiment,
and then execute related commands.

Execute Command
^^^^^^^^^^^^^^^
The other command other than 'plugins' should follow after loading the experiment::

    mrfmsim command [options]

For detailed options, use ``mrfmsim command --help``.

The available commands for experiments:

- ``run``: execute the job (job defined using ``--job job_file`` option)
- ``visualize``: view the experiment model graph
- ``metadata``: show the experiment model metadata
- ``template``: create a template job file based on the experiment
