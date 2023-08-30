output "RDS_address" {
  description = "RDS Endpoint Address"
  value       = aws_db_instance.house-of-plants-short-term-rds.endpoint
}

output "RDS_address" {
  description = "RDS Endpoint Address"
  value       = aws_db_instance.house-of-plants-long-term-rds.endpoint
}


output "ecs_task_definition_arn"{
    description = "ARN for ECS"
    value = aws_ecs_task_definition.house-of-plants-pipeline-ecs.arn
}