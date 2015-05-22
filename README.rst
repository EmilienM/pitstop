pitstop
=====

pitstop aims to calculate, compute and generate an upgrade workflow by using Puppet, Ansible, and RPM.


rpmqal
------

List all the files managed by all packages installed on a RPM-based system.

Example::

    $ python rpmqal.py > content.list

compare_chroots
---------------

Compare the file difference between 2 chroot folders::

    $ python compare_chroots.py old_chroot_dir new_chroot_dir > updated-files.list


file2rpm
--------

Convert a list of files into a list of packages list that manage these files::

    $ python file2rpm.py content.list < updated-files.list > packages_that_need_updates.list


compute_ansible
---------------

Generate a YAML file that defines which snippets we will use for each Puppet class present on nodes we upgrade.
You need to provide upgrade.yaml file that defines an association between Ansible snippets and Puppet classes.

An example is provided in this repository and here is how to use it::

    $ python compute_ansible.py upgrade.yaml <host> > ansible.yaml


list_ansible_snippets
---------------------

Generate a YAML file that defines which snippets we will really use for each Puppet class present on nodes we upgrade.
This YAML file is actually the final artifact we may want to use, because it show up what we need to do (with Ansible) for each service (Puppet class) to upgrade
our platform.

Example::

    $ python list_ansible_snippets.py ansible.yaml new_chroot_dir > ansible-full.yaml 2> error-full
