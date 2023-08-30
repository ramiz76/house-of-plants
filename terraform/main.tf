provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecr_repository" "house-of-plants-ecr" {
  name = "house-of-plants-ecr"
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

# resource "aws_ecs_cluster" "house-of-plants-cluster" {
#   name = "house-of-plants-cluster"
# }




resource "aws_security_group" "house-of-plants-ecs-sg" {
  name   = "house-of-plants-ecs-sg"
  vpc_id = "vpc-0e0f897ec7ddc230d"
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_iam_role" "house-of-plants-ecs-execution-role"{
    name = "house-of-plants-ecs-execution-role"
    assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
        {
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Sid = ""
            Principal = {
                Service = "ecs.amazonaws.com"
            }
        },
    ]
    })

}

# resource "aws_ecs_task_definition" "house-of-plants-pipeline-ecs"{
#     family = "house-of-plants-pipeline-ecs"
#     cpu = "1024"
#     network_mode = "awsvpc"
#     memory = "3072"
#     requires_compatibilities = ["FARGATE"]
#     execution_role_arn = aws_iam_role.house-of-plants-ecs-execution-role.arn

#     container_definitions= jsonencode([
#         {
#             "name": "to be determined",
#             "image": "to be determined",
#             "portMappings": [
#                 {
#                     "name": "443-mapping",
#                     "cpu":0,
#                     "containerPort": 443,
#                     "hostPort": 443,
#                     "protocol": "tcp",
#                     "appProtocol": "https"
#                 },
#                 {
#                     "name": "8501-mapping",
#                     "containerPort": 8501,
#                     "hostPort": 8501,
#                     "protocol": "tcp",
#                     "appProtocol": "http"
#                 }
#             ],
#             "essential": true,
#             "environment": [
#                 {
#                     "name": "DATABASE_NAME",
#                     "value": var.DATABASE_NAME
#                 },
#                 {
#                     "name": "DATABASE_USERNAME",
#                     "value": var.DATABASE_USERNAME
#                 },
#                 {
#                     "name": "DATABASE_ENDPOINT",
#                     "value": aws_db_instance.house-of-plants-rds.endpoint
#                 },
#                 {
#                     "name": "DATABASE_PASSWORD",
#                     "value": var.DATABASE_PASSWORD
#                 }],
#             "logConfiguration": {
#                 "logDriver": "awslogs",
#                 "options": {
#                     "awslogs-create-group": "true",
#                     "awslogs-group": "/ecs/",
#                     "awslogs-region": "eu-west-2",
#                     "awslogs-stream-prefix": "ecs"
#                 }
#             }
#         }
#     ])
# }
