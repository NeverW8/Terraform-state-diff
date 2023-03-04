# Terraform State Diff

A Python script to compare a Terraform state file with the resources provisioned on AWS or Azure.
## Requirements

  *  Python 3.6 or later
  *  Boto3 (for AWS resources)
  *  Azure SDK for Python (azure-mgmt) (for Azure resources)
  *  An AWS account and credentials with permission to access EC2 resources
  *  An Azure account and credentials with permission to access virtual machines, subnets, and resources

## Installation

  1.  Clone the repository or download the terraform_state_diff.py file.

  2. Install the required dependencies by running the following command:
```
pip install boto3 azure-mgmt-compute azure-mgmt-network azure-mgmt-resource
```
  3. Set the AZURE_SUBSCRIPTION_ID environment variable to your Azure subscription ID:

```
    export AZURE_SUBSCRIPTION_ID=<your_subscription_id>
```
> Replace <your_subscription_id> with your actual subscription ID.

## Usage

Run the script with the following command:

```
python terraform_state_diff.py <path_to_state_file>
```
> Replace <path_to_state_file> with the path to your Terraform state file.

The script will compare the resources provisioned on AWS and Azure with the resources in the state file and generate a diff report in JSON format. The report will contain three keys:

  *  aws_only: Resources that exist only in AWS and are not present in the state file.
  *  azure_only: Resources that exist only in Azure and are not present in the state file.
  *  modified: Resources that exist in both AWS/Azure and the state file but have different properties.

The modified key will contain a nested dictionary with the state key representing the state file properties and the aws or azure key representing the properties of the resource in AWS or Azure.
Contributing

Contributions are welcome! Please open an issue or pull request for any bugs or feature requests.
License
