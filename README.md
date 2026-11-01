# Testpress Server Automation with Cloud-Init

Automated, cloud-independent server provisioning using **cloud-init** and **Multipass** on Ubuntu 24.04 LTS.

---

## 1. How to Launch and Reproduce

Run these commands on your host machine to provision the server from scratch:

```bash
# 1. Launch the Ubuntu 24.04 VM with cloud-init
multipass launch 24.04 \
  --name testpress-server \
  --cpus 2 \
  --memory 2G \
  --disk 10G \
  --cloud-init cloud-init.yaml

# 2. Wait until cloud-init provisioning finishes
multipass exec testpress-server -- cloud-init status --wait

# 3. Find the VM IP address
multipass info testpress-server

# 4. Access the application
curl http://<VM_IP>:8080/
# Output: Hello from Testpress!
```

---

## 2. Verification Commands & Expected Outputs

| Requirement | Verification Command | Expected Output |
| :--- | :--- | :--- |
| **HTTP Response** | `curl -i http://<VM_IP>:8080/` | `HTTP/1.0 200 OK`<br>`Hello from Testpress!` |
| **User & Docker Group** | `multipass exec testpress-server -- sudo -u testpress docker ps` | Shows running `testpress-app` container without needing sudo |
| **App Directory & Env** | `multipass exec testpress-server -- cat /opt/testpress/app.env` | `APP_NAME=Testpress`<br>`APP_PORT=8080`<br>`APP_ENV=production` |
| **Systemd Service** | `multipass exec testpress-server -- systemctl status testpress-app` | `Active: active (running)` |
| **Container Health** | `multipass exec testpress-server -- docker inspect --format='{{.State.Health.Status}}' testpress-app` | `healthy` |
| **Reboot Test** | `multipass restart testpress-server`<br>Wait 10s, then `curl http://<VM_IP>:8080/` | `Hello from Testpress!` (starts automatically on boot) |
| **Idempotency** | `multipass exec testpress-server -- sudo cloud-init modules --mode=final` | Completes with exit code `0` without breaking or duplicating |

---

## 3. Cloud-Init Stages & Boot Behavior

Cloud-init handles provisioning across 5 main boot stages:

- **Generator**: Checks early in systemd boot whether cloud-init should run.
- **Local**: Runs before networking is up to discover local data sources (NoCloud).
- **Network**: Runs after network is online to set the hostname and parse configs.
- **Config**: Creates users, groups, and writes initial files (`write_files`).
- **Final**: Installs apt packages and runs commands in `runcmd`.

**What runs when?**
- **First boot only (`per-instance`)**: User creation, package installs, file generation, and `runcmd`. Cloud-init saves completion markers in `/var/lib/cloud/instances/<id>/sem/` so these are skipped on future boots.
- **Every boot (`per-boot`)**: Runtime checks like network verification and dynamic mounts.

---

## 4. Notes & Bonus Questions

- **Systemd service**: Created `/etc/systemd/system/testpress-app.service` to manage the container. This handles starting the container on boot, stopping it cleanly, and restarting it automatically if it crashes (`Restart=always`).
- **Health check**: Added a `HEALTHCHECK` rule in the `Dockerfile` using Python's standard `urllib` library to ping `http://localhost:8080/` every 30 seconds.
- **First boot detection**: Cloud-init looks at `/var/lib/cloud/instance/` and compares the cached `instance-id` with the current one. If it's missing or changed, cloud-init treats the machine as a fresh install.
- **Cloud-init vs Dockerfile**: Cloud-init configures the VM itself (OS, users, storage, system services). A Dockerfile packages the app and its dependencies into a portable container image.
- **User-data vs Metadata**: *Metadata* is machine information supplied by the hypervisor/cloud (IP, instance ID, hostname). *User-data* is the script or `#cloud-config` we pass in to customize the server.

---

## 5. Cleanup

To delete and remove the VM:
```bash
multipass delete testpress-server --purge
```
