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

1. **Create health resource**:
   - Click "Actions" → "Create Resource"
   - Resource Name: `health`
   - Resource Path: `/health`
   - Check "Enable API Gateway CORS"
   - Click "Create Resource"

2. **Create items resource**:
   - Click "Actions" → "Create Resource"
   - Resource Name: `items`
   - Resource Path: `/items`
   - Check "Enable API Gateway CORS"
   - Click "Create Resource"

3. **Create items/{id} resource**:
   - Select the `/items` resource
   - Click "Actions" → "Create Resource"
   - Resource Name: `item-id`
   - Resource Path: `/{id}`
   - Check "Enable API Gateway CORS"
   - Click "Create Resource"

4. **Set up GET method for /health**:
   - Select the `/health` resource
   - Click "Actions" → "Create Method"
   - Select `GET` from dropdown
   - Click the checkmark
   - Integration type: `Lambda Function`
   - Check "Use Lambda Proxy integration"
   - Lambda Function: `aws-gateway-backend`
   - Click "Save"
   - Click "OK" to give API Gateway permission to invoke Lambda

5. **Set up GET method for /items**:
   - Select the `/items` resource
   - Click "Actions" → "Create Method"
   - Select `GET` from dropdown
   - Integration type: `Lambda Function`
   - Check "Use Lambda Proxy integration"
   - Lambda Function: `aws-gateway-backend`
   - Click "Save"

6. **Set up POST method for /items**:
   - Select the `/items` resource
   - Click "Actions" → "Create Method"
   - Select `POST` from dropdown
   - Integration type: `Lambda Function`
   - Check "Use Lambda Proxy integration"
   - Lambda Function: `aws-gateway-backend`
   - Click "Save"

7. **Set up PUT method for /items/{id}**:
   - Select the `/items/{id}` resource
   - Click "Actions" → "Create Method"
   - Select `PUT` from dropdown
   - Integration type: `Lambda Function`
   - Check "Use Lambda Proxy integration"
   - Lambda Function: `aws-gateway-backend`
   - Click "Save"

8. **Set up DELETE method for /items/{id}**:
   - Select the `/items/{id}` resource
   - Click "Actions" → "Create Method"
   - Select `DELETE` from dropdown
   - Integration type: `Lambda Function`
   - Check "Use Lambda Proxy integration"
   - Lambda Function: `aws-gateway-backend`
   - Click "Save"

9. **Set up OPTIONS methods for CORS**:
   - For each resource (`/health`, `/items`, `/items/{id}`):
     - Select the resource
     - Click "Actions" → "Create Method"
     - Select `OPTIONS` from dropdown
     - Integration type: `Mock`
     - Click "Save"

### Step 3: Enable CORS (if not working)

1. **Enable CORS for each resource**:
   - For `/health` resource:
     - Select the `/health` resource
     - Click "Actions" → "Enable CORS"
     - Access-Control-Allow-Origin: `*`
     - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
     - Access-Control-Allow-Methods: `GET,OPTIONS`
     - Click "Enable CORS and replace existing CORS headers"

   - For `/items` resource:
     - Select the `/items` resource
     - Click "Actions" → "Enable CORS"
     - Access-Control-Allow-Origin: `*`
     - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
     - Access-Control-Allow-Methods: `GET,POST,OPTIONS`
     - Click "Enable CORS and replace existing CORS headers"

   - For `/items/{id}` resource:
     - Select the `/items/{id}` resource
     - Click "Actions" → "Enable CORS"
     - Access-Control-Allow-Origin: `*`
     - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
     - Access-Control-Allow-Methods: `PUT,DELETE,OPTIONS`
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
   - Build and test settings should auto-detect from `amplify.yml`
   
   **About amplify.yml file**:
   The `amplify.yml` file in your project root contains the build configuration for AWS Amplify. It defines:
   - Build phases (preBuild, build, postBuild)
   - Artifact location and files to include
   - Cache configuration
   - Environment variables
   
   Example `amplify.yml` configuration:
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
   backend:
     phases:
       preBuild:
         commands:
           - cd backend
           - pip install -r requirements.txt -t .
       build:
         commands:
           - zip -r ../lambda_function.zip .
   ```
   
   **Key sections explained**:
   - `frontend.phases.preBuild`: Commands run before building (install dependencies)
   - `frontend.phases.build`: Commands to build the application
   - `frontend.artifacts.baseDirectory`: Directory containing build output (`dist` for Vite, `build` for Create React App)
   - `frontend.artifacts.files`: Files to include in deployment
   - `frontend.cache.paths`: Directories to cache between builds
   - `backend`: Optional backend build configuration for Lambda deployments
   
   - Verify or modify build commands if needed
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
   
   Expected response:
   ```json
   {
     "statusCode": 200,
     "message": "Health check successful",
     "timestamp": "2024-01-01T12:00:00Z"
   }
   ```

2. **Get all items (empty initially)**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/items
   ```
   
   Expected response:
   ```json
   {
     "statusCode": 200,
     "data": []
   }
   ```

3. **Create an item**:
   ```bash
   curl -X POST https://your-api-url.amazonaws.com/dev/items \
   -H "Content-Type: application/json" \
   -d '{"name":"Test Item","description":"Testing Lambda","category":"test","price":9.99}'
   ```
   
   Expected response:
   ```json
   {
     "statusCode": 200,
     "message": "Item created successfully",
     "data": {
       "id": "item-123",
       "name": "Test Item",
       "description": "Testing Lambda",
       "category": "test",
       "price": 9.99,
       "created_at": "2024-01-01T12:00:00Z"
     }
   }
   ```

4. **Get all items (with data)**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/items
   ```
   
   Expected response:
   ```json
   {
     "statusCode": 200,
     "data": [
       {
         "id": "item-123",
         "name": "Test Item",
         "description": "Testing Lambda",
         "category": "test",
         "price": 9.99,
         "created_at": "2024-01-01T12:00:00Z"
       }
     ]
   }
   ```

5. **Update an item**:
   ```bash
   curl -X PUT https://your-api-url.amazonaws.com/dev/items/item-123 \
   -H "Content-Type: application/json" \
   -d '{"name":"Updated Item","description":"Updated description","category":"updated","price":19.99}'
   ```
   
   Expected response:
   ```json
   {
     "statusCode": 200,
     "message": "Item updated successfully",
     "data": {
       "id": "item-123",
       "name": "Updated Item",
       "description": "Updated description",
       "category": "updated",
       "price": 19.99,
       "updated_at": "2024-01-01T12:05:00Z"
     }
   }
   ```

6. **Delete an item**:
   ```bash
   curl -X DELETE https://your-api-url.amazonaws.com/dev/items/item-123
   ```
   
   Expected response:
   ```json
   {
     "statusCode": 200,
     "message": "Item deleted successfully"
   }
   ```

7. **Test error handling (non-existent item)**:
   ```bash
   curl -X PUT https://your-api-url.amazonaws.com/dev/items/non-existent \
   -H "Content-Type: application/json" \
   -d '{"name":"Test"}'
   ```
   
   Expected response:
   ```json
   {
     "statusCode": 404,
     "error": "Item not found"
   }
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

## 🧪 Comprehensive Test Scenarios

### Scenario 1: Complete CRUD Operations

1. **Start with health check**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/health
   ```

2. **Create multiple items**:
   ```bash
   # Item 1
   curl -X POST https://your-api-url.amazonaws.com/dev/items \
   -H "Content-Type: application/json" \
   -d '{"name":"Laptop","description":"Gaming laptop","category":"electronics","price":1299.99}'

   # Item 2
   curl -X POST https://your-api-url.amazonaws.com/dev/items \
   -H "Content-Type: application/json" \
   -d '{"name":"Coffee Mug","description":"Ceramic mug","category":"kitchenware","price":15.99}'
   ```

3. **Retrieve all items**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/items
   ```

4. **Update first item** (replace `item-id` with actual ID from response):
   ```bash
   curl -X PUT https://your-api-url.amazonaws.com/dev/items/{item-id} \
   -H "Content-Type: application/json" \
   -d '{"name":"Gaming Laptop","description":"High-end gaming laptop","category":"electronics","price":1399.99}'
   ```

5. **Delete second item**:
   ```bash
   curl -X DELETE https://your-api-url.amazonaws.com/dev/items/{item-id}
   ```

6. **Verify final state**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/items
   ```

### Scenario 2: Error Handling Tests

1. **Test invalid JSON**:
   ```bash
   curl -X POST https://your-api-url.amazonaws.com/dev/items \
   -H "Content-Type: application/json" \
   -d '{"name":"Invalid JSON"'
   ```
   Expected: 400 Bad Request

2. **Test missing required fields**:
   ```bash
   curl -X POST https://your-api-url.amazonaws.com/dev/items \
   -H "Content-Type: application/json" \
   -d '{}'
   ```
   Expected: 400 Bad Request

3. **Test non-existent item update**:
   ```bash
   curl -X PUT https://your-api-url.amazonaws.com/dev/items/non-existent-id \
   -H "Content-Type: application/json" \
   -d '{"name":"Test"}'
   ```
   Expected: 404 Not Found

4. **Test non-existent item deletion**:
   ```bash
   curl -X DELETE https://your-api-url.amazonaws.com/dev/items/non-existent-id
   ```
   Expected: 404 Not Found

### Scenario 3: Load Testing

1. **Create multiple items rapidly**:
   ```bash
   for i in {1..10}; do
     curl -X POST https://your-api-url.amazonaws.com/dev/items \
     -H "Content-Type: application/json" \
     -d "{\"name\":\"Item $i\",\"description\":\"Test item $i\",\"category\":\"test\",\"price\":$((i * 10)).99}" &
   done
   wait
   ```

2. **Verify all items were created**:
   ```bash
   curl https://your-api-url.amazonaws.com/dev/items
   ```

### Scenario 4: Integration Testing with Frontend

1. **Open frontend in browser**
2. **Update API URL field** with your actual API Gateway URL
3. **Test health check** - should show green status
4. **Create items using the form**:
   - Name: "Frontend Test Item"
   - Description: "Created via frontend"
   - Category: "test"
   - Price: 29.99
5. **Verify item appears in the items list**
6. **Edit the item** using the edit functionality
7. **Delete the item** using the delete button
8. **Test error scenarios**:
   - Submit form with empty fields
   - Try to edit/delete non-existent items

### Scenario 5: CORS Testing

1. **Test from different origins** (if you have multiple domains):
   ```javascript
   // Run in browser console from different domain
   fetch('https://your-api-url.amazonaws.com/dev/health')
     .then(response => response.json())
     .then(data => console.log(data))
     .catch(error => console.error('CORS Error:', error));
   ```

2. **Test preflight requests**:
   ```bash
   curl -X OPTIONS https://your-api-url.amazonaws.com/dev/items \
   -H "Origin: https://example.com" \
   -H "Access-Control-Request-Method: POST" \
   -H "Access-Control-Request-Headers: Content-Type"
   ```

### Test Results Validation

✅ **Success Indicators**:
- Health check returns 200 status
- All CRUD operations work correctly
- Proper error responses (400, 404, 500) for invalid requests
- CORS headers present in responses
- Frontend can communicate with backend
- Items persist across requests

❌ **Failure Indicators**:
- 502/503 errors (Lambda/Gateway issues)
- CORS errors in browser console
- Timeout errors (check Lambda timeout settings)
- 403 errors (permission issues)
- Inconsistent responses

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
   - Re-enable CORS on each individual resource (`/health`, `/items`, `/items/{id}`)
   - Ensure OPTIONS methods are created for each resource
   - Redeploy API after CORS changes
   - Check that Access-Control-Allow-Methods includes the specific HTTP methods for each resource

2. **404 errors**:
   - Verify resource paths match exactly (`/health`, `/items`, `/items/{id}`)
   - Check that all HTTP methods (GET, POST, PUT, DELETE) are created on appropriate resources
   - Ensure Lambda proxy integration is enabled for each method
   - Verify the stage deployment includes all resources

3. **500 errors**:
   - Check Lambda logs in CloudWatch (`/aws/lambda/aws-gateway-backend`)
   - Verify Lambda function name is correct in each method integration
   - Check Lambda function permissions (API Gateway invoke permission)
   - Test Lambda function directly in AWS console

4. **Method not allowed (405) errors**:
   - Ensure the correct HTTP method is configured on the right resource
   - For example: PUT and DELETE should be on `/items/{id}`, not `/items`
   - Check that OPTIONS method exists for CORS preflight

5. **Resource not found errors**:
   - Verify resource hierarchy: root → /health, root → /items → /{id}
   - Check that resource paths don't have leading/trailing slashes inconsistencies
   - Ensure stage deployment includes all new resources

### Common Amplify Issues

1. **Build failures**:
   - Check build logs in Amplify console
   - Verify package.json has correct scripts
   - Ensure `amplify.yml` has correct build commands
   - Check `amplify.yml` syntax (proper YAML indentation)
   - Verify `baseDirectory` points to correct build output folder (`dist` for Vite, `build` for CRA)

2. **amplify.yml configuration issues**:
   - **Wrong baseDirectory**: Make sure it matches your build tool:
     - Vite: `baseDirectory: dist`
     - Create React App: `baseDirectory: build`
     - Next.js: `baseDirectory: out` (if using static export)
   - **Missing dependencies**: Ensure `npm ci` or `npm install` is in preBuild commands
   - **Build command mismatch**: Verify build command matches package.json scripts
   - **Cache issues**: Clear cache or modify cache paths if builds are inconsistent
   - **Environment variables**: Add them to amplify.yml if needed:
     ```yaml
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

3. **Backend section in amplify.yml** (if deploying Lambda via Amplify):
   - Ensure Python dependencies are installed correctly
   - Verify zip command creates proper structure
   - Check that `requirements.txt` exists and is valid

4. **API connection issues**:
   - Verify API URL is correct in frontend
   - Check CORS settings on API Gateway
   - Ensure environment variables are properly set
   - Test API endpoints independently before frontend integration

5. **Deployment issues**:
   - **Branch mismatch**: Ensure Amplify is watching the correct branch
   - **Build timeout**: Increase build timeout in Amplify settings if builds are slow
   - **Memory issues**: Large builds might need memory optimization
   - **File size limits**: Check if artifacts exceed Amplify limits

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