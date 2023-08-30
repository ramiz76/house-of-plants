provider "aws" {
  region = "eu-west-2"
}


resource "aws_security_group" "house-of-plants-rds-sg" {
  name        = "house-of-plants-rds-sg"
  description = "RDS Security Group"
  vpc_id      = "vpc-0e0f897ec7ddc230d"

  ingress {
    description = "TLS from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

resource "aws_db_instance" "house-of-plants-rds" {

  instance_class         = "db.t3.micro"
  identifier             = "house-of-plants-rds"
  allocated_storage      = 20
  engine                 = "postgres"
  username               = var.DATABASE_USERNAME
  password               = var.DATABASE_PASSWORD
  publicly_accessible    = true
  skip_final_snapshot    = true
  db_subnet_group_name   = "public_subnet_group"
  vpc_security_group_ids = [resource.aws_security_group.house-of-plants-rds-sg.id]
  availability_zone      = "eu-west-2a"
  db_name                = var.DATABASE_NAME
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "house-of-plants-ec2"

  instance_type          = "t2.micro"
  key_name               = "radl_key_pair"
  monitoring             = true
  vpc_security_group_ids = [resource.aws_security_group.house-of-plants-rds-sg.id]
  subnet_id              = "subnet-"

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}