# -*- coding: utf-8 -*-
import pulumi
from typing import Any, Optional
from pulumi import ResourceOptions
from pulumi_aws import eks

from timberstone_cloud_sdk.kubernetes import iam, vpc
from timberstone_cloud_sdk.kubernetes.utils import generate_kube_config


class Cluster:
    def __init__(
        self,
        cluster_name: Optional[str] = None,
        opts: ResourceOptions = None,
        **kwargs: Any
    ):

        self.cluster = eks.Cluster(
            resource_name=cluster_name,
            role_arn=iam.eks_role.arn,
            tags={
                "Name": cluster_name,
            },
            vpc_config=eks.ClusterVpcConfigArgs(
                public_access_cidrs=["0.0.0.0/0"],
                security_group_ids=[vpc.eks_security_group.id],
                subnet_ids=vpc.subnet_ids,
            ),
        )
        self.node_group = eks.NodeGroup(
            "eks-node-group",
            cluster_name=self.cluster.name,
            node_group_name="pulumi-eks-nodegroup",
            node_role_arn=iam.ec2_role.arn,
            subnet_ids=vpc.subnet_ids,
            tags={
                "Name": "pulumi-cluster-nodeGroup",
            },
            scaling_config=eks.NodeGroupScalingConfigArgs(
                desired_size=2,
                max_size=2,
                min_size=1,
            ),
        )
        pulumi.export("cluster-name", self.cluster.name)
        pulumi.export("kubeconfig", generate_kube_config(self.cluster))
