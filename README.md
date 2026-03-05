# ☁️ The Cloud Resume Challenge

This project is my implementation of **The Cloud Resume Challenge** — a 16-step project that bridges cloud certification with real-world DevOps skills.

The result is a fully serverless, production-grade portfolio site with a live visitor counter, HTTPS, custom domain, infrastructure as code, and an automated CI/CD pipeline. No servers. No manual deployments. No hardcoded credentials.

**Why it matters for FinOps:** As a FinOps professional, hands-on cloud experience directly strengthens the conversations I have with Engineering and Product teams. You can only get so far advising on cloud costs from a spreadsheet. At some point, you have to build something.

## 💡 Why This Project

FinOps sits at the intersection of Finance and DevOps — maximizing the business value of cloud spend. That means working closely with engineering teams who are building the infrastructure that drives the bill.

This project was about closing the gap between the work I analyze and the work I advise on. Building it gave me:

- Firsthand experience with the architectural decisions that drive cloud costs
- A working understanding of serverless tradeoffs (Lambda Function URL vs. API Gateway — see cost analysis below)
- Practical IaC and CI/CD experience in a real production environment
- A foundation for every cloud project that follows

## 🏗️ Solution Architecture

```text
┌─────────────────────────────────────────────────────┐
│                      User                           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Amazon Route 53                        │  ← DNS (custom domain)
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│             Amazon CloudFront                       │  ← CDN + HTTPS termination
│          + AWS Certificate Manager                  │  ← Free TLS certificate
└──────────┬───────────────────────────┬──────────────┘
           │                           │
           ▼                           ▼
┌─────────────────────┐    ┌────────────────────────────┐
│   Amazon S3         │    │  Lambda Function URL       │  ← Visitor counter API
│  (Static Assets)    │    │  (No API Gateway needed)   │
└─────────────────────┘    └────────────────┬───────────┘
                                            │
                                            ▼
                               ┌────────────────────────┐
                               │     Amazon DynamoDB    │  ← Visitor count store
                               └────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              GitHub Actions (CI/CD)                 │  ← Auto-deploy on push
│              + OIDC (no stored credentials)         │
└─────────────────────────────────────────────────────┘
```

### Request Flow

1. **DNS** → User hits `theprojectfolder.com`, Route 53 resolves to CloudFront
2. **CDN** → CloudFront serves cached assets from nearest edge location
3. **HTTPS** → ACM certificate handles TLS — no manual cert management
4. **Static assets** → HTML, CSS, images served from S3 origin (CloudFront handles egress)
5. **Visitor counter** → JavaScript triggers POST to Lambda Function URL
6. **Backend** → Lambda atomically increments DynamoDB counter and returns count
7. **Display** → Frontend renders visitor count

## ✨ Key Features

Built with ☁️ AWS, 🐍 Python, ☕ stubbornness, and the willingness to delete everything and start over.

### Frontend
- 🌐 **Custom domain** with HTTPS via Route 53 + ACM
- ⚡ **Global CDN delivery** via CloudFront (100 GB/month free tier)
- 📊 **Live visitor counter** — real-time, serverless
- 📱 **Responsive design** — works on all devices

### Backend
- ⚡ **Lambda Function URL** — replaces API Gateway for single-endpoint use case
- 🗄️ **DynamoDB On-Demand** — elastic scaling, no capacity planning
- 🔒 **IAM least-privilege** — Lambda role scoped to specific table operations only
- 🌐 **CORS configured** — locked to production domain origin

### Infrastructure & DevOps
- 📦 **Infrastructure as Code** — CloudFormation templates for reproducible deploys
- 🔄 **CI/CD pipeline** — GitHub Actions auto-deploys on push to `main`
- 🔑 **OIDC authentication** — no long-lived AWS credentials stored in GitHub
- 🏷️ **Resource tagging** — all resources tagged `Project: CloudResume` for cost visibility

## 🛠️ Technology Stack

### AWS Services

| Service | Role |
|---------|------|
| **S3** | Static website hosting (HTML, CSS, JS, images, resume PDF) |
| **CloudFront** | CDN, HTTPS termination, edge caching |
| **AWS Certificate Manager** | Free TLS certificate, auto-renewal |
| **Route 53** | DNS management, custom domain |
| **Lambda** | Serverless visitor counter backend (Python) |
| **DynamoDB** | Visitor count persistence (On-Demand, Standard table) |
| **CloudFormation** | Infrastructure as Code |
| **IAM** | Roles and policies (OIDC for GitHub, Lambda execution role) |

### Languages & Tools

| Tool | Use |
|------|-----|
| **HTML5 / CSS3** | Frontend site |
| **JavaScript (ES6+)** | Visitor counter fetch calls |
| **Python 3.x** | Lambda function |
| **CloudFormation (YAML)** | Infrastructure as Code |
| **GitHub Actions** | CI/CD pipeline |
| **AWS CLI** | Local deployment and debugging |

## 💰 Cost Analysis

### The Real Monthly Cost

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| **S3 Storage** | 5 GB / 12 mo (then $0.023/GB) | $0.00 |
| **S3 GET Requests** | 20K/mo free | $0.00 |
| **CloudFront Data Transfer** | 100 GB/mo free (permanent†) | $0.00 |
| **CloudFront Requests** | 1M req/mo free (permanent†) | $0.00 |
| **ACM Certificate** | Always free | $0.00 |
| **Lambda Requests** | 1M req/mo free (permanent) | $0.00 |
| **Lambda Compute** | 400K GB-seconds/mo free (permanent) | $0.00 |
| **DynamoDB** | 25 WCU/RCU provisioned free | $0.00 |
| **Route 53 Hosted Zone** | — | $0.50 |
| **Route 53 DNS Queries** | First 1B queries/mo: $0.40/million | ~$0.00 |
| **Total Monthly** | | **~$0.50** |

*† CloudFront Free tier updated November 2025 — permanent, not the 12-month trial*

- **Domain registration:** ~$13/year (one-time annual cost via Route 53)
- **Effective annual cost:** $6 (hosted zone) + $13 (domain) = **$19/year**

### Lambda Function URL vs. API Gateway

The challenge originally prescribes API Gateway. I replaced it with a Lambda Function URL. Here's why:

| Feature | Lambda Function URL | API Gateway (HTTP API) |
|---------|---------------------|------------------------|
| **Cost (10K visitors/mo)** | $0.00 | ~$0.01 |
| **Cost (1M visitors/mo)** | $0.00 | ~$1.00 |
| **Request pricing** | Included in Lambda free tier | $1.00/million (after free tier) |
| **Advanced features** | IAM auth only | Auth, throttling, stages, logging |
| **Setup complexity** | Simple | Moderate |
| **Right for this use case?** | ✅ Yes | ❌ Overengineered |

**FinOps decision:** One endpoint. One operation. Lambda Function URL is the right-sized solution. API Gateway adds cost and complexity for features a visitor counter doesn't need. If I add multiple routes or need rate limiting, I'll revisit.
