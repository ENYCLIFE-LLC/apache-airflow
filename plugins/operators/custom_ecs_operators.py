# from airflow.models import BaseOperator
# from airflow.utils.decorators import apply_defaults
# from plugins.hooks.custom_ecs_hook import CustomEcsHook


# class CreateEcsServiceOperator(BaseOperator):
#     @apply_defaults
#     def __init__(self, cluster_name, service_name, task_definition, subnets, security_groups, target_group_arn, container_name, container_port, region_name, *args, **kwargs):
#         super(CreateEcsServiceOperator, self).__init__(*args, **kwargs)
#         self.cluster_name = cluster_name
#         self.service_name = service_name
#         self.task_definition = task_definition
#         self.subnets = subnets
#         self.security_groups = security_groups
#         self.target_group_arn = target_group_arn
#         self.container_name = container_name
#         self.container_port = container_port
#         self.region_name = region_name

#     def execute(self, context):
#         hook = CustomEcsHook(region_name=self.region_name)
#         service = hook.describe_service(self.cluster_name, self.service_name)
#         if not service['services'] or service['services'][0]['status'] == 'INACTIVE':
#             hook.create_service(
#                 self.cluster_name,
#                 self.service_name,
#                 self.task_definition,
#                 self.subnets,
#                 self.security_groups,
#                 self.target_group_arn,
#                 self.container_name,
#                 self.container_port
#             )
#             self.log.info("Service created and started")
#         else:
#             self.log.info("Service already exists and is active")


# class ScaleUpEcsServiceOperator(BaseOperator):
#     @apply_defaults
#     def __init__(self, cluster_name, service_name, region_name, *args, **kwargs):
#         super(ScaleUpEcsServiceOperator, self).__init__(*args, **kwargs)
#         self.cluster_name = cluster_name
#         self.service_name = service_name
#         self.region_name = region_name

#     def execute(self, context):
#         hook = CustomEcsHook(region_name=self.region_name)
#         service = context['task_instance'].xcom_pull(task_ids='check_ecs_service')
#         if service and (service['desiredCount'] == 0 or service['runningCount'] == 0):
#             hook.update_service(self.cluster_name, self.service_name, desired_count=1)
#             self.log.info("Service scaled up to desired count of 1")
#         else:
#             self.log.info("Service is already running")


# class CreateEcsServiceOperator(BaseOperator):
#     @apply_defaults
#     def __init__(self, cluster_name, service_name, task_definition, subnets, security_groups, region_name, *args, **kwargs):
#         super(CreateEcsServiceOperator, self).__init__(*args, **kwargs)
#         self.cluster_name = cluster_name
#         self.service_name = service_name
#         self.task_definition = task_definition
#         self.subnets = subnets
#         self.security_groups = security_groups
#         self.region_name = region_name

#     def execute(self, context):
#         hook = CustomEcsHook(region_name=self.region_name)
#         service = context['task_instance'].xcom_pull(task_ids='check_ecs_service')
#         if not service:
#             hook.create_service(self.cluster_name, self.service_name, self.task_definition, self.subnets, self.security_groups)
#             self.log.info("Service created and started")
#         else:
#             self.log.info("Service already exists")


# class CallApiOperator(BaseOperator):
#     @apply_defaults
#     def __init__(self, http_conn_id, endpoint, method='GET', headers=None, *args, **kwargs):
#         super(CallApiOperator, self).__init__(*args, **kwargs)
#         self.http_conn_id = http_conn_id
#         self.endpoint = endpoint
#         self.method = method
#         self.headers = headers

#     def execute(self, context):
#         response = self.http_hook.run(self.endpoint, method=self.method, headers=self.headers)
#         context['task_instance'].xcom_push(key='api_response', value=response.text)
#         self.log.info("API called successfully")
#         return response.text
