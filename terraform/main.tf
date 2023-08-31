provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecr_repository" "house-of-plants-short-term-ecr" {
  name = "house-of-plants-short-term-ecr"
}

resource "aws_ecr_repository" "house-of-plants-long-term-ecr" {
  name = "house-of-plants-long-term-ecr"
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


resource "aws_ecs_cluster" "house-of-plants-cluster" {
  name = "house-of-plants-cluster"
}

resource "aws_s3_bucket" "house-of-plants-long-term-storage" {
  bucket = "house-of-plants-long-term-storage"
}


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

# resource "aws_iam_role" "house-of-plants-ecs-execution-role" {
#   name = "house-of-plants-ecs-execution-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Action = "sts:AssumeRole",
#         Effect = "Allow",
#         Sid    = "",
#         Principal = {
#           Service = "ecs.amazonaws.com"
#         }
#       },

#     ]
#   })
#   inline_policy {
#     name = "ecs-task-inline-policy"
#     policy = jsonencode({
#       Version = "2012-10-17",
#       Statement = [
#         {
#           Action   = "ecs:DescribeTaskDefinition",
#           Effect   = "Allow",
#           Resource = "*"
#         },
#         {
#           Action   = "ecs:DescribeTasks",
#           Effect   = "Allow",
#           Resource = "*"
#         },
#         {
#           Action   = "ecs:RunTask",
#           Effect   = "Allow",
#           Resource = "*"
#         }
#       ]
#     })
#   }
# }



resource "aws_ecs_task_definition" "house-of-plants-short-pipeline-ecs" {
  family                   = "house-of-plants-short-pipeline-def"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = "arn:aws:iam::129033205317:role/ecs_role"
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"

  container_definitions = jsonencode([
    {
      "name" : "house-of-plants-short-pipeline",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/house-of-plants-short-term-ecr:latest",
      "portMappings" : [
        {
          "name" : "443-mapping",
          "cpu" : 0,
          "containerPort" : 443,
          "hostPort" : 443,
          "protocol" : "tcp",
          "appProtocol" : "http"
        },
        {
          "name" : "8501-mapping",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "DATABASE_NAME",
          "value" : var.DATABASE_NAME
        },
        {
          "name" : "DATABASE_USERNAME",
          "value" : var.DATABASE_USERNAME
        },
        {
          "name" : "DATABASE_ENDPOINT",
          "value" : aws_db_instance.house-of-plants-rds.endpoint
        },
        {
          "name" : "DATABASE_PASSWORD",
          "value" : var.DATABASE_PASSWORD
      }],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-create-group" : "true",
          "awslogs-group" : "/ecs/",
          "awslogs-region" : "eu-west-2",
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}


resource "aws_ecs_task_definition" "house-of-plants-long-pipeline-ecs" {
  family                   = "house-of-plants-long-pipeline-def"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = "arn:aws:iam::129033205317:role/ecs_role"
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"

  container_definitions = jsonencode([
    {
      "name" : "house-of-plants-long-pipeline",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/house-of-plants-long-term-ecr:latest",
      "portMappings" : [
        {
          "name" : "443-mapping",
          "cpu" : 0,
          "containerPort" : 443,
          "hostPort" : 443,
          "protocol" : "tcp",
          "appProtocol" : "http"
        },
        {
          "name" : "8501-mapping",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "DATABASE_NAME",
          "value" : var.DATABASE_NAME
        },
        {
          "name" : "DATABASE_USERNAME",
          "value" : var.DATABASE_USERNAME
        },
        {
          "name" : "DATABASE_ENDPOINT",
          "value" : aws_db_instance.house-of-plants-rds.endpoint
        },
        {
          "name" : "ACCESS_KEY_ID",
          "value" : var.ACCESS_KEY_ID
        },
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : var.SECRET_ACCESS_KEY
        },
        {
          "name" : "S3_BUCKET",
          "value" : var.S3_BUCKET
        },
        {
          "name" : "DATABASE_PASSWORD",
          "value" : var.DATABASE_PASSWORD
      }],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-create-group" : "true",
          "awslogs-group" : "/ecs/",
          "awslogs-region" : "eu-west-2",
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}





# resource "aws_iam_role" "scheduled-short-assume-role-policy" {
#   name = "scheduled-short-assume-role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Action = "sts:AssumeRole",
#         Effect = "Allow",
#         Principal = {
#           Service = "ecs-tasks.amazonaws.com"
#         }
#       }
#     ]
#   })
# }


resource "aws_scheduler_schedule" "house-of-plants-short-schedule" {
  name       = "house-of-plants-short-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 minute)"

  target {
    arn      = aws_ecs_cluster.house-of-plants-cluster.arn
    role_arn = "arn:aws:iam::129033205317:role/service-role/Amazon_EventBridge_Scheduler_ECS_3c99621ce2"
    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.house-of-plants-short-pipeline-ecs.arn
      launch_type         = "FARGATE"
      task_count          = 1
      network_configuration {
        assign_public_ip = true
        subnets          = ["subnet-03b1a3e1075174995", "subnet-0667517a2a13e2a6b", "subnet-0cec5bdb9586ed3c4"]
        security_groups  = [aws_security_group.house-of-plants-ecs-sg.id]
      }
    }
  }
}

resource "aws_scheduler_schedule" "house-of-plants-long-schedule" {
  name       = "house-of-plants-long-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(6 hours)"

  target {
    arn      = aws_ecs_cluster.house-of-plants-cluster.arn
    role_arn = "arn:aws:iam::129033205317:role/service-role/Amazon_EventBridge_Scheduler_ECS_3c99621ce2"
    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.house-of-plants-long-pipeline-ecs.arn
      launch_type         = "FARGATE"
      task_count          = 1
      network_configuration {
        assign_public_ip = true
        subnets          = ["subnet-03b1a3e1075174995", "subnet-0667517a2a13e2a6b", "subnet-0cec5bdb9586ed3c4"]
        security_groups  = [aws_security_group.house-of-plants-ecs-sg.id]
      }
    }
  }
}















# resource "aws_ecs_task_definition" "house-of-plants-short-dashboard"{
#     family = "house-of-plants-short-dashboard"
#     cpu = "1024"
#     network_mode = "awsvpc"
#     memory = "3072"
#     requires_compatibilities = ["FARGATE"]
#     execution_role_arn = aws_iam_role.house-of-plants-ecs-execution-role.arn

#     container_definitions= jsonencode([
#         {
#             "name": "short-term-dashboard",
#             "image": "to be determined",
#             "portMappings": [
#                 {
#                     "name": "short-term-dashboard-80-tcp",
#                     "cpu":0,
#                     "containerPort": 80,
#                     "hostPort": 80,
#                     "protocol": "tcp",
#                     "appProtocol": "http"
#                 },
#                 {
#                     "name": "short-term-dashboard-8501-tcp",
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
#                     "value": aws_db_instance.house-of-plants-short-term-rds.endpoint
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

