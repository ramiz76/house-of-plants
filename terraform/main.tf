provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecr_repository" "house-of-plants-short-term-ecr" {
  name = "house-of-plants-short-term-ecr"
}

resource "aws_ecr_repository" "house-of-plants-long-term-ecr" {
  name = "house-of-plants-long-term-ecr"
}

resource "aws_ecr_repository" "house-of-plants-long-dashboard-ecr" {
  name = "house-of-plants-long-dashboard-ecr"
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


resource "aws_iam_role" "ecs-task-execution-role" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      },

      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "scheduler.amazonaws.com",
          "Condition" : {
            "StringEquals" : {
              "aws:SourceAccount" : "129033205317"
          } }
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
  inline_policy {
    name = "ecs-task-inline-policy"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Action   = "ecs:DescribeTaskDefinition",
          Effect   = "Allow",
          Resource = "*",
          Condition = {
            "ArnLike" : {
              "ecs:cluster" : "arn:aws:ecs:*:129033205317:cluster/house-of-plants-cluster"
            }
          }
        },
        {
          Action   = "ecs:DescribeTasks",
          Effect   = "Allow",
          Resource = "*",
          Condition = {
            "ArnLike" : {
              "ecs:cluster" : "arn:aws:ecs:*:129033205317:cluster/house-of-plants-cluster"
            }
          }
        },
        {
          Action   = "ecs:RunTask",
          Effect   = "Allow",
          Resource = "*",
          Condition = {
            "ArnLike" : {
              "ecs:cluster" : "arn:aws:ecs:*:129033205317:cluster/house-of-plants-cluster"
            }
          }
        },
        {
          Action   = "iam:PassRole",
          Effect   = "Allow",
          Resource = "*"
        }
      ]
    })
  }

}

resource "aws_iam_role_policy_attachment" "ecs-task-execution-role-policy-attachment" {
  role       = aws_iam_role.ecs-task-execution-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}



resource "aws_iam_role" "ecs-task-role-policy" {
  name = "ecs-task-role-policy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })

}

resource "aws_iam_role_policy_attachment" "ecs-task-read-bucket-policy" {
  role       = aws_iam_role.ecs-task-role-policy.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}



resource "aws_ecs_task_definition" "house-of-plants-short-pipeline-ecs" {
  family                   = "house-of-plants-short-pipeline-definition"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = aws_iam_role.ecs-task-role-policy.arn
  execution_role_arn       = aws_iam_role.ecs-task-execution-role.arn

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
          "value" : aws_db_instance.house-of-plants-rds.address
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
  family                   = "house-of-plants-long-pipeline-definition"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = aws_iam_role.ecs-task-role-policy.arn
  execution_role_arn       = aws_iam_role.ecs-task-execution-role.arn

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
          "value" : aws_db_instance.house-of-plants-rds.address
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
          "name" : "BUCKET_NAME",
          "value" : var.BUCKET_NAME
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


resource "aws_ecs_task_definition" "house-of-plants-long-dashboard-ecs" {
  family                   = "house-of-plants-long-dashboard-ecs"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = aws_iam_role.ecs-task-role-policy.arn
  execution_role_arn       = aws_iam_role.ecs-task-execution-role.arn

  container_definitions = jsonencode([
    {
      "name" : "house-of-plants-dashboard",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/house-of-plants-long-dashboard-ecr:latest",
      "portMappings" : [
        {
          "name" : "8501-mapping",
          "containerPort" : 8501,
          "hostPort" : 8501,
          "protocol" : "tcp",
          "appProtocol" : "http"
        },
        {
          "name" : "80-mapping",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "ACCESS_KEY_ID",
          "value" : var.ACCESS_KEY_ID
        },
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : var.SECRET_ACCESS_KEY
        },
        {
          "name" : "BUCKET_NAME",
          "value" : var.BUCKET_NAME
        }
      ],
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


resource "aws_security_group" "house-of-plants-long-dashboard-sg" {
  name   = "house-of-plants-long-dashboard-sg"
  vpc_id = "vpc-0e0f897ec7ddc230d"
  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
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

resource "aws_ecs_service" "house-of-plants-long-dashboard-service" {
  name            = "house-of-plants-long-dashboard-service"
  cluster         = aws_ecs_cluster.house-of-plants-cluster.id
  task_definition = aws_ecs_task_definition.house-of-plants-long-dashboard-ecs.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = ["subnet-03b1a3e1075174995", "subnet-0cec5bdb9586ed3c4", "subnet-0667517a2a13e2a6b"]
    security_groups  = [aws_security_group.house-of-plants-long-dashboard-sg.id]
    assign_public_ip = true
  }
}


resource "aws_scheduler_schedule" "house-of-plants-short-schedule" {
  name       = "house-of-plants-short-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(* * * * ? *)"

  target {
    arn      = aws_ecs_cluster.house-of-plants-cluster.arn
    role_arn = aws_iam_role.ecs-task-execution-role.arn
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

  schedule_expression = "cron(0 */6 * * ? *)"

  target {
    arn      = aws_ecs_cluster.house-of-plants-cluster.arn
    role_arn = aws_iam_role.ecs-task-execution-role.arn
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

