import pulumi_aws as aws

current = aws.get_region()

# Creating a VPC and a public subnet
app_vpc = aws.ec2.Vpc("app-vpc",
    cidr_block="172.31.0.0/16",
    enable_dns_hostnames=True)

app_vpc_subnet = aws.ec2.Subnet(
    "app-vpc-subnet",
    cidr_block="172.31.0.0/20",
    availability_zone=current.name + "a",
    vpc_id=app_vpc)

# Creating a gateway to the web for the VPC
app_gateway = aws.ec2.InternetGateway("app-gateway",
    vpc_id=app_vpc.id)

app_routetable = aws.ec2.RouteTable("app-routetable",
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=app_gateway.id,
        )
    ],
    vpc_id=app_vpc.id)

# Associating our gateway with our VPC to allow the MySQL database to communicate 
# with the internet
app_routetable_association = aws.ec2.MainRouteTableAssociation("app_routetable_association",
    route_table_id=app_routetable.id,
    vpc_id=app_vpc)

# Creating a Security Group that restricts incoming traffic to HTTP
app_security_group = aws.ec2.SecurityGroup("security-group",
	vpc_id=app_vpc.id,
	description="Enables HTTP access",
    ingress=[aws.ec2.SecurityGroupIngressArgs(
		protocol="tcp",
		from_port=0,
		to_port=65535,
		cidr_blocks=["0.0.0.0/0"],
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
		protocol="-1",
		from_port=0,
		to_port=0,
		cidr_blocks=["0.0.0.0/0"],
    )])

# Creating an RDS instance requires having two subnets
extra_rds_subnet = aws.ec2.Subnet("extra-rds-subnet",
    cidr_block="172.31.128.0/20",
    availability_zone=current.name + "b",
    vpc_id=app_vpc)

# Both subnets are assigned to a SubnetGroup used by the RDS instance
app_database_subnetgroup = aws.rds.SubnetGroup("app-database-subnetgroup",
    subnet_ids=[app_vpc_subnet.id, extra_rds_subnet.id])