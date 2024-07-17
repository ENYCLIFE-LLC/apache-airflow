AWS provides a broad range of services that support event-driven architectures. These services can trigger actions or workflows based on specific events, allowing you to build responsive and scalable applications. Here is a list of key AWS services that are commonly used for event-driven architectures:

### 1. **Amazon EventBridge**
- **Description**: A serverless event bus service that allows you to connect your applications using data from your own applications, integrated SaaS applications, and AWS services.
- **Use Cases**: Routing events to AWS Lambda, Step Functions, and other AWS services; integrating with third-party SaaS applications.

### 2. **AWS Lambda**
- **Description**: A serverless compute service that runs your code in response to events and automatically manages the compute resources for you.
- **Use Cases**: Running code in response to events from other AWS services (e.g., S3, DynamoDB, Kinesis, SNS, CloudWatch Events).

### 3. **Amazon Simple Notification Service (SNS)**
- **Description**: A fully managed messaging service for both application-to-application (A2A) and application-to-person (A2P) communication.
- **Use Cases**: Sending notifications to multiple subscribers; triggering AWS Lambda functions.

### 4. **Amazon Simple Queue Service (SQS)**
- **Description**: A fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.
- **Use Cases**: Queueing messages for processing by AWS Lambda, EC2 instances, or other consumers.

### 5. **Amazon S3 Event Notifications**
- **Description**: Allows you to receive notifications when certain events happen in your S3 bucket, such as object creation or deletion.
- **Use Cases**: Triggering AWS Lambda functions or SQS messages when files are uploaded or deleted from an S3 bucket.

### 6. **Amazon DynamoDB Streams**
- **Description**: Captures a time-ordered sequence of item-level changes in a DynamoDB table and sends these changes to a stream.
- **Use Cases**: Triggering AWS Lambda functions to process changes in DynamoDB tables; data replication.

### 7. **Amazon Kinesis**
- **Description**: A platform for streaming data on AWS, including services like Kinesis Data Streams, Kinesis Data Firehose, and Kinesis Data Analytics.
- **Use Cases**: Real-time data processing, streaming analytics, and feeding data into AWS Lambda or other services.

### 8. **AWS Step Functions**
- **Description**: A serverless orchestration service that lets you coordinate multiple AWS services into serverless workflows.
- **Use Cases**: Orchestrating complex workflows, handling retries and parallel execution, integrating with AWS Lambda and other services.

### 9. **Amazon CloudWatch Events**
- **Description**: Delivers a near real-time stream of system events that describe changes in AWS resources.
- **Use Cases**: Triggering AWS Lambda functions or Step Functions based on events from AWS resources or scheduled cron jobs.

### 10. **AWS CodePipeline**
- **Description**: A continuous integration and continuous delivery service for fast and reliable application and infrastructure updates.
- **Use Cases**: Automating the build, test, and deploy phases of your release process whenever there is a code change.

### 11. **AWS CodeBuild**
- **Description**: A fully managed build service that compiles source code, runs tests, and produces software packages that are ready to deploy.
- **Use Cases**: Automatically starting builds based on commits to a code repository.

### 12. **Amazon RDS Event Notifications**
- **Description**: Provides notifications for Amazon RDS events to subscribed SNS topics.
- **Use Cases**: Receiving alerts about database events, such as backup completion, failover, or replication state changes.

### 13. **Amazon ECS Event Stream**
- **Description**: Delivers near real-time notifications of changes in your Amazon ECS clusters.
- **Use Cases**: Monitoring cluster state changes, triggering workflows based on container instance events.

### 14. **AWS IoT Events**
- **Description**: A fully managed service that makes it easy to detect and respond to events from IoT sensors and applications.
- **Use Cases**: Monitoring and responding to IoT sensor data, automating workflows based on sensor events.

### 15. **AWS Glue**
- **Description**: A fully managed ETL (extract, transform, and load) service that makes it easy to prepare and load data for analytics.
- **Use Cases**: Running ETL jobs based on triggers such as new data arrival in S3.

These services can be used individually or combined to create complex event-driven architectures, enabling your applications to respond promptly and efficiently to a wide variety of events.