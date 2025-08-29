# 🚀 AWS Setup Guide: Lambda + API Gateway + Amplify

This guide will walk you through deploying your React frontend to AWS Amplify and your Python backend to AWS Lambda with API Gateway.

## 📋 Prerequisites

1. **AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **AWS CLI**: Install from [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. **Node.js**: Install from [nodejs.org](https://nodejs.org)
4. **Git**: For version control

## 🔧 AWS CLI Configuration

1. **Configure AWS CLI**:
   ```bash
   aws configure
   ```
   Enter your:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Default output format (`json`)

2. **Verify configuration**:
   ```bash
   aws sts get-caller-identity
   ```

## 🐍 Part 1: Deploy Lambda Function

### Step 1: Create Lambda Deployment Package

1. **Navigate to backend directory**:
   ```bash
   cd AWS_gateway/backend
   ```

2. **Install dependencies locally**:
   ```bash
   pip install -r requirements.txt -t .
   ```

3. **Create deployment package**:
   ```bash
   zip -r lambda_function.zip .
   ```

### Step 2: Create Lambda Function via AWS Console

1. **Go to AWS Lambda Console**:
   - Navigate to [AWS Lambda Console](https://console.aws.amazon.com/lambda)
   - Click "Create function"

2. **Configure function**:
   - Choose "Author from scratch"
   - Function name: `aws-gateway-backend`
   - Runtime: `Python 3.11`
   - Architecture: `x86_64`
   - Click "Create function"

3. **Upload code**:
   - In the "Code" section, click "Upload from" → ".zip file"
   - Upload your `lambda_function.zip`
   - Click "Save"

4. **Configure function settings**:
   - Go to "Configuration" → "General configuration"
   - Set timeout to `30 seconds`
   - Set memory to `256 MB`
   - Click "Save"

### Step 3: Test Lambda Function

1. **Create test event**:
   - Click "Test" → "Create new event"
   - Event name: `health-check`
   - Use this JSON:
   ```json
   {
     "httpMethod": "GET",
     "path": "/health",
     "queryStringParameters": null,
     "body": null
   }
   ```

2. **Run test**:
   - Click "Test"
   - Verify response shows success

## 🌐 Part 2: Set Up API Gateway

### Step 1: Create API Gateway

1. **Go to API Gateway Console**:
   - Navigate to [API Gateway Console](https://console.aws.amazon.com/apigateway)
   - Click "Create API"

2. **Choose API type**:
   - Select "REST API" (not private)
   - Click "Build"

3. **Configure API**:
   - API name: `aws-gateway-api`
   - Description: `API for testing Lambda backend`
   - Endpoint Type: `Regional`
   - Click "Create API"

### Step 2: Create Resources and Methods

1. **Create proxy resource**:
   - Click "Actions" → "Create Resource"
   - Check "Configure as proxy resource"
   - Resource Name: `proxy`
   - Resource Path: `{proxy+}`
   - Check "Enable API Gateway CORS"
   - Click "Create Resource"

2. **Set up ANY method**:
   - The ANY method should be automatically created
   - Click on "ANY"
   - Integration type: `Lambda Function`
   - Check "Use Lambda Proxy integration"
   - Lambda Function: `aws-gateway-backend`
   - Click "Save"
   - Click "OK" to give API Gateway permission to invoke Lambda

### Step 3: Enable CORS (if not working)

1. **Select your proxy resource**:
   - Click on `/{proxy+}`

2. **Enable CORS**:
   - Click "Actions" → "Enable CORS"
   - Access-Control-Allow-Origin: `*`
   - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
   - Access-Control-Allow-Methods: `GET,POST,PUT,DELETE,OPTIONS`
   - Click "Enable CORS and replace existing CORS headers"

### Step 4: Deploy API

1. **Deploy API**:
   - Click "Actions" → "Deploy API"
   - Deployment stage: `[New Stage]`
   - Stage name: `dev`
   - Click "Deploy"

2. **Get API URL**:
   - Copy the "Invoke URL" (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/dev`)
   - This is your API Gateway URL!

### Step 5: Test API

1. **Test health endpoint**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/health
   ```

2. **Test with browser**:
   - Open your API URL + `/health` in browser
   - Should see JSON response

## ⚛️ Part 3: Deploy Frontend to Amplify

### Step 1: Prepare Frontend

1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Update API URL in App.jsx**:
   - Replace the default API URL with your actual API Gateway URL
   - Line 8 in `src/App.jsx`:
   ```javascript
   const [apiUrl, setApiUrl] = useState('https://your-actual-api-url.amazonaws.com/dev')
   ```

4. **Test locally**:
   ```bash
   npm run dev
   ```

5. **Build for production**:
   ```bash
   npm run build
   ```

### Step 2: Create Git Repository

1. **Initialize git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub/GitLab** (create repository first):
   ```bash
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

### Step 3: Deploy with Amplify

1. **Go to AWS Amplify Console**:
   - Navigate to [AWS Amplify Console](https://console.aws.amazon.com/amplify)
   - Click "Get started" under "Amplify Hosting"

2. **Connect repository**:
   - Choose your Git provider (GitHub/GitLab/etc.)
   - Authorize AWS Amplify
   - Select your repository
   - Select branch (`main`)
   - Click "Next"

3. **Configure build settings**:
   - App name: `aws-gateway-frontend`
   - Build and test settings should auto-detect
   - Verify build commands:
     ```yaml
     version: 1
     frontend:
       phases:
         preBuild:
           commands:
             - npm ci
         build:
           commands:
             - npm run build
       artifacts:
         baseDirectory: dist
         files:
           - '**/*'
       cache:
         paths:
           - node_modules/**/*
     ```
   - Click "Next"

4. **Review and deploy**:
   - Review settings
   - Click "Save and deploy"

5. **Wait for deployment**:
   - Wait for build to complete (5-10 minutes)
   - Get your Amplify URL

## 🧪 Part 4: Testing Everything

### Step 1: Test Backend Directly

1. **Health check**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/health
   ```

2. **Create an item**:
   ```bash
   curl -X POST https://your-api-url.amazonaws.com/dev/items \
   -H "Content-Type: application/json" \
   -d '{"name":"Test Item","description":"Testing Lambda","category":"test","price":9.99}'
   ```

3. **Get all items**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/items
   ```

### Step 2: Test Frontend

1. **Open Amplify URL**:
   - Navigate to your Amplify app URL
   - Should see the testing interface

2. **Update API URL**:
   - Paste your actual API Gateway URL in the input field
   - Test health check first

3. **Test all methods**:
   - Try creating items with POST
   - Get items with GET
   - Update items with PUT
   - Delete items with DELETE

## 🔍 Troubleshooting

### Common Lambda Issues

1. **Timeout errors**:
   - Increase Lambda timeout in Configuration → General configuration

2. **Permission errors**:
   - Check Lambda execution role has basic permissions

3. **Import errors**:
   - Ensure all dependencies are in the zip file

### Common API Gateway Issues

1. **CORS errors**:
   - Re-enable CORS on all resources
   - Redeploy API after CORS changes

2. **404 errors**:
   - Check resource paths match exactly
   - Ensure proxy integration is enabled

3. **500 errors**:
   - Check Lambda logs in CloudWatch
   - Verify Lambda function name in API Gateway

### Common Amplify Issues

1. **Build failures**:
   - Check build logs in Amplify console
   - Verify package.json has correct scripts

2. **API connection issues**:
   - Verify API URL is correct in frontend
   - Check CORS settings

## 📊 Monitoring and Logs

### Lambda Logs
- Go to CloudWatch → Log groups → `/aws/lambda/aws-gateway-backend`

### API Gateway Logs
- Enable logging in API Gateway stage settings
- View logs in CloudWatch

### Amplify Logs
- Check build logs in Amplify console

## 💰 Cost Optimization

1. **Lambda**: 1M free requests/month
2. **API Gateway**: 1M free requests/month
3. **Amplify**: 1000 build minutes/month, 15GB storage
4. **CloudWatch**: 5GB log storage free

## 🎉 Success!

If everything is working:
- ✅ Lambda function responds to requests
- ✅ API Gateway routes requests to Lambda
- ✅ Frontend communicates with backend
- ✅ All HTTP methods work (GET, POST, PUT, DELETE)

Your AWS full-stack application is now live! 🚀

## 📚 Next Steps

1. **Add a database**: Integrate DynamoDB for persistent storage
2. **Add authentication**: Use AWS Cognito
3. **Add monitoring**: Set up CloudWatch alarms
4. **Add custom domain**: Use Route 53 and SSL certificates
5. **Add CI/CD**: Set up automated deployments

## 🆘 Need Help?

- AWS Documentation: [docs.aws.amazon.com](https://docs.aws.amazon.com)
- AWS Support Forums: [forums.aws.amazon.com](https://forums.aws.amazon.com)
- Stack Overflow: Tag questions with `aws-lambda`, `aws-api-gateway`, `aws-amplify`