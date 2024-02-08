mrfmsim-cli
======================

The *mrfmsim-cli* package is part of the 
`mrfmsim project <https://marohn-group.github.io/mrfmsim-docs/>`__. 
The package is loaded as a plugin and provides quick command-line actions
for the *mrfmsim* packages.


To see the commands and options::

    mrfmsim --help

To list all available plugins::

    mrfmsim plugins


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
