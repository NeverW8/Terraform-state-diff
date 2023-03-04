import json
import os
import argparse
from collections import defaultdict
from typing import Dict, List

import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient


def load_state_file(state_file: str) -> Dict:
    with open(state_file, "r") as f:
        return json.load(f)


def get_aws_resources() -> List[Dict]:
    client = boto3.client("ec2")
    response = client.describe_instances()
    instances = response["Reservations"]
    return instances


def get_azure_resources() -> Dict:
    credential = DefaultAzureCredential()
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)
    resource_client = ResourceManagementClient(credential, subscription_id)

    vms = compute_client.virtual_machines.list_all()
    subnets = network_client.subnets.list_all()
    resources = resource_client.resources.list()

    resources_by_type = defaultdict(list)
    for resource in resources:
        resources_by_type[resource.type].append(resource)

    return {
        "vms": list(vms),
        "subnets": list(subnets),
        "other_resources": resources_by_type,
    }


def compare_resources(state: Dict, aws_resources: List[Dict], azure_resources: Dict):
    diff = {
        "aws_only": {},
        "azure_only": {},
        "modified": {},
    }

    # Compare AWS resources
    for resource in aws_resources:
        if "InstanceId" not in resource:
            continue
        instance_id = resource["InstanceId"]
        if instance_id not in state["resources"]:
            diff["aws_only"][instance_id] = resource
        else:
            resource_state = state["resources"][instance_id]
            if resource_state != resource:
                diff["modified"][instance_id] = {
                    "state": resource_state,
                    "aws": resource,
                }

    # Compare Azure resources
    for resource_type, resources in azure_resources.items():
        for resource in resources:
            resource_id = resource.id
            if resource_id not in state["resources"]:
                diff["azure_only"][resource_id] = {
                    "type": resource_type,
                    "resource": resource.as_dict(),
                }
            else:
                resource_state = state["resources"][resource_id]
                if resource_state != resource.as_dict():
                    diff["modified"][resource_id] = {
                        "state": resource_state,
                        "azure": resource.as_dict(),
                    }

    return diff


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare Terraform state file with AWS and Azure resources")
    parser.add_argument("state_file", type=str, help="Path to the Terraform state file")
    args = parser.parse_args()

    state = load_state_file(args.state_file)
    aws_resources = get_aws_resources()
    azure_resources = get_azure_resources()

    diff = compare_resources(state, aws_resources, azure_resources)

    print(json.dumps(diff, indent=2))
    
