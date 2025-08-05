
## Project Overview: Coworking Space Service

The Coworking Space Service is a set of APIs that enables users to request one-time tokens and administrators to authorize access to a coworking space. This service follows a microservice pattern and the APIs are split into distinct services that can be deployed and managed independently of one another. For this project, you are a DevOps engineer who will be collaborating with a team that is building an API for business analysts. The API provides business analysts with basic analytics data on user activity in the coworking space service. The application they provide you functions as expected, and you will help build a pipeline to deploy it to Kubernetes. You'll submit artefacts from the build and deployment of this service.

## Step 1: Spawn the infrastructure
Infrastructure consists of AWS EKS, an ECR Repository and a VPC with a public subnet.
Fork this repository, and set up your AWS credentials in Github then launch the Github pipeline.
https://github.com/m-ghanem-dev/coworking-space-project-infrastructure


## Step 2: Deploy the application
Run the Github actions workflow in this repository. 
- It will apply the K8s manifests needed to run Postgres on Kubernetes 
(a Persistent Volume, a Persistent Volume Claim to request using the persistent volume backend by gp2 storage and the postgres service).

- Then it will build the docker image for the application and push it to the backend repository in ECR 

- Then it will utilize kustomize to enforce that Kubernetes pulls the latest image.

## Step 3: Run the application
Get the DNS name of the loadbalancer and visit the endpoint /api/reports/daily_usage or /health_check
