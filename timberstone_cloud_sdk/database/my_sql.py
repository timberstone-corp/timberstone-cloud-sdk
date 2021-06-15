# Copyright 2016-2020, Pulumi Corporation.  All rights reserved.

import json
import base64
import pulumi
import pulumi_aws as aws
import pulumi_mysql as mysql

from pulumi import ResourceOptions, ComponentResource
from typing import Any

from timberstone_cloud_sdk.database import mysql_dynamic_provider, vpc


class Database(ComponentResource):
    def __init__(self, 
                 resource_name: str,
                 config: pulumi.Config,
                 opts: ResourceOptions = None,
                 **kwargs: Any):
        self.resource_name = resource_name

        # Get neccessary settings from the pulumi config
        self.config = config
        self.admin_name = config.require("sql-admin-name")
        self.admin_password = config.require_secret("sql-admin-password")
        self.user_name = config.require("sql-user-name")
        self.user_password = config.require_secret("sql-user-password")
        self.availability_zone = aws.config.region


        # An RDS instnace is created to hold our MySQL database
        mysql_rds_server = aws.rds.Instance("mysql-server",
            engine="mysql",
            username=self.admin_name,
            password=self.admin_password,
            instance_class="db.t2.micro",
            allocated_storage=20,
            skip_final_snapshot=True,
            publicly_accessible=True,
            db_subnet_group_name=vpc.app_database_subnetgroup.id,
            vpc_security_group_ids=[vpc.app_security_group.id])

        # Creating a Pulumi MySQL provider to allow us to interact with the RDS instance
        mysql_provider = mysql.Provider("mysql-provider",
            endpoint=mysql_rds_server.endpoint,
            username=self.admin_name,
            password=self.admin_password)

        # Initializing a basic database on the RDS instance
        mysql_database = mysql.Database("mysql-database",
            name="votes-database",
            opts=pulumi.ResourceOptions(provider=mysql_provider))

        # Creating a user which will be used to manage MySQL tables 
        mysql_user = mysql.User("mysql-standard-user",
            user=self.user_name,
            host="example.com",
            plaintext_password=self.user_password,
            opts=pulumi.ResourceOptions(provider=mysql_provider))

        # The user only needs the "SELECT" and "UPDATE" permissions to function
        mysql_access_grant = mysql.Grant("mysql-access-grant",
            user=mysql_user.user,
            host=mysql_user.host,
            database=mysql_database.name,
            privileges= ["SELECT", "UPDATE"],
            opts=pulumi.ResourceOptions(provider=mysql_provider))

        # The database schema and initial data to be deployed to the database
        creation_script = """
            CREATE TABLE votesTable (
                choice_id int(10) NOT NULL AUTO_INCREMENT,
                vote_count int(10) NOT NULL,
                PRIMARY KEY (choice_id)
            ) ENGINE=InnoDB;
            INSERT INTO votesTable(choice_id, vote_count) VALUES (0,0);
            INSERT INTO votesTable(choice_id, vote_count) VALUES (1,0);
            """

        # The SQL commands the database performs when deleting the schema
        deletion_script = "DROP TABLE votesTable CASCADE"

        # Creating our dynamic resource to deploy the schema during `pulumi up`. The arguments
        # are passed in as a SchemaInputs object
        mysql_votes_table = mysql_dynamic_provider.Schema(name="mysql_votes_table",
            args=mysql_dynamic_provider.SchemaInputs(self.admin_name, self.admin_password, mysql_rds_server.address, mysql_database.name, creation_script, deletion_script))

        # Exporting the ID of the dynamic resource we created
        pulumi.export("dynamic-resource-id",mysql_votes_table.id)