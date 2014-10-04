Using configuration files
=========================

To ease the repition and remembering all the :doc:`/run-arguments`, it is
possible to store these configuration options in a ``.dockerrpm`` file which
resides together with either the ``.spec`` or ``.srpm`` file.

There are currently two sections of configuration that is supported in ``.dockerrpm``:

* rpmbuild
* docker

The first one is for configuring details about which docker image to use as
base, where to find source archive to unpack etc. The second section is
configuration that will be passed directly to the `docker client api
<https://pypi.python.org/pypi/docker-py>`_. This could be details such as where
to find the docker socket etc.

The format of the configuration file is in ``.ini`` file format!


Options for configuring the rpmbuild execution
----------------------------------------------
 
``define`` can be set multiple times in the config.

``source`` can be set multiple times in the config.

``sources_dir`` can be set instead of ``source``. This is usally the `SOURCES/` directory in a default rpmdev build tree.

``macrofile`` can be set multiple times in the config, and `macrofiles` will reside together with the `spec` file in `SPECS/`

``retrieve`` can be set to either true or false. If set to true this will trigger to run `spectool` to download the source(s) and patch(es) that are defined in the `spec` file. 

``output`` can be set where you want to extract the `rpm` and `srpm` files that has been built inside the docker container.

``image`` is a docker image which will be used as a base building image. 

For further details, see :doc:`Dockerfile </dockerfile>`

Options for configuring docker client
-------------------------------------

``base_url`` is used for passing the information for where the docker server is
hosted. Format is protocol+hostname+port. 

``version`` which API level the docker server is using.

``timeout`` specifies the HTTP request timeout in seconds towards the docker
server.
