# Oracle Cloud Setup Guide for Phase-V

**Purpose**: Provision and configure Oracle Cloud Always Free infrastructure for Phase-V deployment

**Date**: 2026-02-19

**Version**: 1.0.0

---

## Overview

This guide provides step-by-step instructions for provisioning Oracle Cloud Always Free resources and deploying the Phase-V application to Oracle Cloud Compute instances.

### Oracle Cloud Always Free Tier Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| OCPUs | 2 OCPUs | Per VM instance |
| RAM | 12 GB | Per VM instance |
| Block Volume | 200 GB | Total |
| Object Storage | 10 GB | Total |
| Load Balancer | 1 (10 Mbps) | Not used in this setup |
| Public IP | 2 ephemeral | Included with compute |

**Our Setup**: 2x VM.Standard.E2.1.Micro instances (1 OCPU, 6GB RAM each)

---

## Prerequisites

### 1. Oracle Cloud Account

- Sign up for Oracle Cloud Free Tier: https://www.oracle.com/cloud/free/
- Verify your account and complete the signup process
- Note your tenancy OCID and user OCID

### 2. OCI CLI Installation

```bash
# Install OCI CLI
curl -o install.sh https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh
chmod +x install.sh
./install.sh

# Verify installation
oci --version

# Configure OCI CLI
oci setup config
```

### 3. Required Permissions

Ensure your user has the following IAM policies:
- `Allow group <your-group> to manage instance-family in compartment <your-compartment>`
- `Allow group <your-group> to manage virtual-network-family in compartment <your-compartment>`
- `Allow group <your-group> to manage security-lists in compartment <your-compartment>`

---

## Step 1: Create Virtual Cloud Network (VCN)

### Via OCI Console

1. Navigate to **Networking > Virtual Cloud Networks**
2. Click **Create VCN**
3. Configure:
   - **Name**: `phase-v-vcn`
   - **Compartment**: Select your compartment
   - **CIDR Block**: `10.0.0.0/16`
   - **DNS Resolution**: Enabled
   - **DNS Label**: `phasev`
4. Click **Create VCN**

### Via OCI CLI

```bash
# Create VCN
oci network vcn create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --display-name phase-v-vcn \
  --cidr-blocks '["10.0.0.0/16"]' \
  --dns-label phasev

# Create Internet Gateway
oci network internet-gateway create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --vcn-id <VCN_OCID> \
  --display-name phase-v-igw \
  --is-enabled true

# Create Route Table
oci network route-table create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --vcn-id <VCN_OCID> \
  --display-name phase-v-route-table \
  --route-rules '[{"destination": "0.0.0.0/0", "destinationType": "CIDR", "networkEntityId": "<INTERNET_GATEWAY_OCID>"}]'

# Create Security List
oci network security-list create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --vcn-id <VCN_OCID> \
  --display-name phase-v-security-list \
  --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 22, "max": 22}}}, {"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 80, "max": 80}}}, {"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 443, "max": 443}}}, {"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 6443, "max": 6443}}}]' \
  --egress-security-rules '[{"destination": "0.0.0.0/0", "protocol": "all"}]'

# Create Subnet
oci network subnet create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --vcn-id <VCN_OCID> \
  --display-name phase-v-subnet \
  --cidr-block 10.0.0.0/24 \
  --route-table-id <ROUTE_TABLE_OCID> \
  --security-list-ids <SECURITY_LIST_OCID> \
  --dns-label phasev
```

---

## Step 2: Create SSH Key Pair

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/phase-v-key -C "phase-v" -N ""

# Set permissions
chmod 600 ~/.ssh/phase-v-key
chmod 644 ~/.ssh/phase-v-key.pub

# The public key will be added to compute instances
cat ~/.ssh/phase-v-key.pub
```

---

## Step 3: Create Compute Instances

### Instance 1: k3s Server

1. Navigate to **Compute > Instances**
2. Click **Create Instance**
3. Configure:
   - **Name**: `phase-v-k3s-server`
   - **Compartment**: Select your compartment
   - **Availability Domain**: Select any
   - **Image**: Oracle Linux 8 or Ubuntu 22.04
   - **Shape**: VM.Standard.E2.1.Micro (Always Free)
   - **Network**: Select `phase-v-vcn` and `phase-v-subnet`
   - **Assign Public IPv4 Address**: Yes
   - **SSH Keys**: Paste your public key content
4. Click **Create**

### Instance 2: k3s Agent

Repeat the above steps with:
- **Name**: `phase-v-k3s-agent`
- **Same VCN and Subnet**
- **Same SSH Key**

### Via OCI CLI

```bash
# Create k3s server instance
oci compute instance launch \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --display-name phase-v-k3s-server \
  --availability-domain <AD> \
  --shape VM.Standard.E2.1.Micro \
  --image-id <UBUNTU_22_04_IMAGE_OCID> \
  --subnet-id <SUBNET_OCID> \
  --assign-public-ip true \
  --ssh-authorized-keys-file ~/.ssh/phase-v-key.pub \
  --metadata '{"user_data": ""}'

# Create k3s agent instance
oci compute instance launch \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --display-name phase-v-k3s-agent \
  --availability-domain <AD> \
  --shape VM.Standard.E2.1.Micro \
  --image-id <UBUNTU_22_04_IMAGE_OCID> \
  --subnet-id <SUBNET_OCID> \
  --assign-public-ip true \
  --ssh-authorized-keys-file ~/.ssh/phase-v-key.pub \
  --metadata '{"user_data": ""}'
```

### Find Ubuntu 22.04 Image OCID

```bash
oci compute image list \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --operating-system "Canonical-Ubuntu-22.04" \
  --sort-by TIMECREATED \
  --sort-order DESC
```

---

## Step 4: Configure Network Security

### Add Required Ingress Rules

Navigate to your VCN's Security List and add:

| Source | Port Range | Protocol | Purpose |
|--------|-----------|----------|---------|
| 0.0.0.0/0 | 22 | TCP | SSH |
| 0.0.0.0/0 | 80 | TCP | HTTP |
| 0.0.0.0/0 | 443 | TCP | HTTPS |
| 0.0.0.0/0 | 6443 | TCP | Kubernetes API |
| 10.0.0.0/16 | 2379-2380 | TCP | etcd |
| 10.0.0.0/16 | 6443 | TCP | Kubernetes API (internal) |
| 10.0.0.0/16 | 8472 | UDP | Flannel VXLAN |
| 10.0.0.0/16 | 10250 | TCP | Kubelet API |

---

## Step 5: Connect to Instances

```bash
# Get public IPs from OCI Console or CLI
SERVER_IP=$(oci compute instance list \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --display-name phase-v-k3s-server \
  --query "data[0].public-ip" --raw-output)

AGENT_IP=$(oci compute instance list \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --display-name phase-v-k3s-agent \
  --query "data[0].public-ip" --raw-output)

# Test SSH connection
ssh -i ~/.ssh/phase-v-key ubuntu@$SERVER_IP
ssh -i ~/.ssh/phase-v-key ubuntu@$AGENT_IP
```

---

## Step 6: Verify Resource Usage

### Check Compute Resources

```bash
# List all instances
oci compute instance list \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --query "data[*].{name:\"display-name\",shape:\"shape\",ad:\"availability-domain\"}"
```

### Check VCN Resources

```bash
# List VCNs
oci network vcn list --compartment-id <YOUR_COMPARTMENT_OCID>

# List subnets
oci network subnet list --compartment-id <YOUR_COMPARTMENT_OCID>
```

---

## Post-Provisioning Steps

After provisioning is complete:

1. **Install k3s**: Run `./scripts/install-k3s.sh`
2. **Install Traefik**: Run `./scripts/install-traefik.sh`
3. **Install cert-manager**: Run `./scripts/install-cert-manager.sh`
4. **Install Dapr**: Run `dapr init -k --wait`
5. **Deploy Application**: Run `./scripts/deploy-cloud.sh`

---

## Cost Estimation

### Always Free Resources (No Cost)

| Resource | Quantity | Monthly Cost |
|----------|----------|-------------|
| VM.Standard.E2.1.Micro | 2 | $0.00 |
| VCN | 1 | $0.00 |
| Block Volume (200GB) | 1 | $0.00 |
| Public IP (Ephemeral) | 2 | $0.00 |
| **Total** | | **$0.00** |

### Potential Costs (If Exceeding Free Tier)

- Additional compute instances: ~$25/month per VM.Standard.E2.1.Micro
- Additional storage: $0.0255/GB/month
- Load Balancer (if used): ~$20/month

---

## Troubleshooting

### Instance Won't Start

1. Check compartment quotas
2. Verify shape availability in the selected AD
3. Ensure you have sufficient free tier resources

### Cannot SSH to Instance

1. Verify security list allows port 22
2. Check SSH key permissions: `chmod 600 ~/.ssh/phase-v-key`
3. Verify public IP is assigned
4. Check instance console connection for boot issues

### Network Connectivity Issues

1. Verify route table has internet gateway
2. Check security list ingress/egress rules
3. Test from within VCN: `ping 10.0.0.x`

---

## Cleanup

To avoid any potential charges, clean up resources when done:

```bash
# Delete compute instances
oci compute instance terminate --instance-id <INSTANCE_OCID> --force

# Delete VCN (this also deletes subnets, gateways, etc.)
oci network vcn delete --vcn-id <VCN_OCID>

# Delete SSH keys
rm ~/.ssh/phase-v-key ~/.ssh/phase-v-key.pub
```

---

## Next Steps

After Oracle Cloud provisioning is complete:

1. ✅ Run `./scripts/install-k3s.sh` to install k3s cluster
2. ✅ Run `./scripts/install-traefik.sh` to install ingress controller
3. ✅ Run `./scripts/install-cert-manager.sh` to install SSL/TLS management
4. ✅ Run `./scripts/deploy-cloud.sh` to deploy Phase-V application
5. ✅ Configure Redpanda Cloud connection
6. ✅ Verify HTTPS endpoint is accessible

---

## References

- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- [OCI CLI Documentation](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
- [Oracle Cloud Compute](https://docs.oracle.com/en-us/iaas/compute/)
- [k3s Documentation](https://docs.k3s.io/)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
