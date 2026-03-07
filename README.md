pangolin-update
=========

Upgrade pangolin & its various dependencies to the latest version, following the recommended upgrade path.

Requirements
------------

- community.docker

Role Variables
--------------

- `pangolin_dir` - Path to pangolin, default: `/home/ansible/pangolin`
- `backup_destination` - Directory to back up pangolin to, default: `/home/ansible/pangolin_backups`

Example Playbook
----------------

```yaml
- name: Update Pangolin
  hosts: pangolin_servers
  roles:
    - role: pangolin-update
      vars:
        pangolin_dir: "/home/ansible/pangolin/"
        backup_destination: "/home/ansible/pangolin_backups/"
```

License
-------

MIT
