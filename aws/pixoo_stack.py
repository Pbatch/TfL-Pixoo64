import os

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk.aws_ecr_assets import DockerImageAsset, Platform
from constructs import Construct


class PixooStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "PixooVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
        )

        instance = ec2.Instance(
            self,
            "PixooServer",
            instance_type=ec2.InstanceType("t4g.nano"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            role=iam.Role(
                self,
                "PixooRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonSSMManagedInstanceCore"
                    )
                ],
            ),
        )

        image_asset = DockerImageAsset(
            self, "PixooImage", directory="../local", platform=Platform.LINUX_ARM64
        )

        image_asset.repository.grant_pull(instance.role)

        instance.add_user_data(
            "dnf update -y",
            "dnf install -y docker",
            "systemctl enable --now docker",
            f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {image_asset.repository.repository_uri}",
            f"docker pull {image_asset.image_uri}",
            f"docker run -d --name pixoo-app --restart always "
            f"-e PIXOO_URL={os.environ.get('PIXOO_URL')} "
            f"-e TFL_APP_KEY={os.environ.get('TFL_APP_KEY')} "
            f"{image_asset.image_uri}",
        )

        CfnOutput(self, "InstanceId", value=instance.instance_id)
