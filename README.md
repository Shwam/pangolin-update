# pangolin-update

An Ansible role that upgrades Pangolin and its companion services (Traefik, Gerbil) to the latest version, following the recommended incremental upgrade path.

---
## How It Works

Pangolin recommends upgrading one major version at a time rather than jumping straight from an old version to the latest. This role automates that process:

1. Reads the current image versions from `docker-compose.yml`
2. Queries Docker Hub for available versions and calculates the correct upgrade path
3. Backs up Pangolin directory before making any changes
4. Updates the image version tags in `docker-compose.yml` one major version at a time
5. Restarts the stack and confirms it comes back healthy
6. Automatically restores the backup if the upgrade fails

> Note: The playbook determines what to upgrade by reading image version tags in `docker-compose.yml`. It automatically skips any service pinned to `latest` since there is no version to step through. If the image is tagged `latest`, it will not be updated by this playbook. To include it in automated updates, pin it to a specific version first (e.g. `crowdsecurity/crowdsec:1.6.8`), then the playbook will pick it up on future runs.

---

## Requirements

**Ansible controller machine** (the machine you run the playbook from):
- Python 3
- Ansible
```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible
```
- `community.docker` collection:
  ```bash
  ansible-galaxy collection install community.docker
  ```

**Pangolin server:**
- The Ansible controller must be able to SSH into the Pangolin server using key-based authentication
- The Ansible user on the Pangolin server must have permission to run `docker compose` commands

---

## SSH Key Setup

If you haven't set up SSH key access to the Pangolin server yet:

```bash
# Generate a key pair on your Ansible controller (skip if you already have one)
ssh-keygen -t ed25519 -C "ansible"

# Copy the public key to the Pangolin server
# Replace <user> and <pangolin-vps-ip> with your actual values
ssh-copy-id <user>@<pangolin-vps-ip>

# Confirm it works
ssh <user>@<pangolin-vps-ip>
```

---

## Inventory Setup

Create an inventory file that tells Ansible where your Pangolin server is and how to connect to it.

Copy the example below and fill in your environment's values:

```yaml
# inventory.yml
all:
  children:
    pangolin_servers:
      hosts:
        # Replace with your Pangolin server's hostname or IP address
        <pangolin-vps-hostname-or-ip>:
          ansible_user: <ssh-user>              # The user Ansible will SSH in as
          pangolin_dir: "/home/ansible/pangolin/"        # Path to your Pangolin directory on the server
          backup_destination: "/home/ansible/pangolin_backups/" # Where backups will be saved
```

**Example:**
```yaml
all:
  children:
    pangolin_servers:
      hosts:
        pangolin.example.com:
          ansible_user: ansible
          pangolin_dir: "/home/ansible/pangolin/"
          backup_destination: "/home/ansible/pangolin_backups/"
```

> Note: The `pangolin_dir` and `backup_destination` paths must exist on the Pangolin server before running the playbook. Create them if they don't:
> ```bash
> mkdir -p /home/ansible/pangolin_backups
> ```
---

## Running the Playbook

**1. Clone this repo onto your Ansible controller:**
```bash
git clone <this-repo-url>
cd pangolin-update
```

**2. Create your inventory file**

**3. Run the playbook:**
```bash
ansible-playbook -i inventory.yml update-pangolin.yml
```

**To see more detail as it runs:**
```bash
ansible-playbook -i inventory.yml update-pangolin.yml -v
```

---

## Example Playbook

If you are incorporating this role into a larger Ansible project rather than using it standalone:

```yaml
- name: Update Pangolin
  hosts: pangolin_servers
  roles:
    - role: pangolin-update
      vars:
        pangolin_dir: "/home/ansible/pangolin/"
        backup_destination: "/home/ansible/pangolin_backups/"
```

---

## License

MIT
