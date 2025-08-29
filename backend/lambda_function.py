"""
AWS Lambda Function for REST API Backend
=========================================

This Lambda function serves as a serverless backend that handles all HTTP methods
(GET, POST, PUT, DELETE) through API Gateway proxy integration.

Key Concepts:
- Serverless: No servers to manage, AWS handles scaling automatically
- Event-driven: Function executes only when triggered by API Gateway
- Stateless: Each invocation is independent (no persistent state between calls)
- Pay-per-use: Only charged for execution time and requests

Architecture Flow:
Frontend (React) → API Gateway → Lambda Function → Response → API Gateway → Frontend
"""

import json
import boto3
from datetime import datetime
import uuid

# ==============================================================================
# GLOBAL STORAGE (In-Memory)
# ==============================================================================
# NOTE: This is for demonstration only!
# In production, use AWS DynamoDB for persistent storage
# Lambda containers are reused for efficiency, so this dict persists
# between invocations for a short time, but it's NOT guaranteed
items_storage = {}

def lambda_handler(event, context):
    """
    Main Lambda Entry Point
    ======================
    
    This is the function AWS Lambda calls when triggered by API Gateway.
    
    Parameters:
    -----------
    event : dict
        Contains all request information from API Gateway:
        - httpMethod: GET, POST, PUT, DELETE, OPTIONS
        - path: /health, /items, /items/123
        - headers: All HTTP headers from client
        - body: Request body (JSON string for POST/PUT)
        - queryStringParameters: URL query params (?category=electronics)
        - pathParameters: URL path variables ({id} in /items/{id})
        
    context : LambdaContext
        Lambda runtime information (request ID, memory limit, etc.)
        Not used in this function but always provided by AWS
        
    Returns:
    --------
    dict
        Response object that API Gateway converts to HTTP response:
        - statusCode: HTTP status (200, 201, 404, 500)
        - headers: HTTP response headers (including CORS)
        - body: JSON string response body
    """
    
    try:
        # ======================================================================
        # REQUEST PARSING
        # ======================================================================
        # Extract key information from the API Gateway event
        http_method = event.get('httpMethod', 'GET')  # Default to GET if missing
        path = event.get('path', '/')                 # Default to root path
        
        print(f"🚀 Processing: {http_method} {path}")  # CloudWatch logging
        
        # ======================================================================
        # CORS HEADERS SETUP
        # ======================================================================
        # Cross-Origin Resource Sharing - allows frontend from different domain
        # to call this API. Essential for React app on localhost to call AWS API
        cors_headers = {
            'Access-Control-Allow-Origin': '*',  # Allow any domain (dev only!)
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        }
        
        # ======================================================================
        # CORS PREFLIGHT HANDLING
        # ======================================================================
        # Browsers send OPTIONS request before actual request for CORS check
        # This is automatic browser behavior for "complex" requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }
        
        # ======================================================================
        # ROUTING LOGIC
        # ======================================================================
        # Route requests to appropriate handlers based on URL path
        # This is like a simple router in web frameworks
        
        if path == '/health':
            # Health check endpoint - useful for monitoring and testing
            return handle_health(event, cors_headers)
            
        elif path == '/items':
            # Collection endpoint - operates on all items
            return handle_items(event, http_method, cors_headers)
            
        elif path.startswith('/items/'):
            # Single resource endpoint - operates on specific item
            # Extract item ID from path: /items/123 → item_id = "123"
            item_id = path.split('/')[-1]  # Get last part after final slash
            return handle_single_item(event, http_method, item_id, cors_headers)
            
        else:
            # 404 - Path not found
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Path not found'})
            }
            
    except Exception as e:
        # ======================================================================
        # GLOBAL ERROR HANDLING
        # ======================================================================
        # Catch any unexpected errors and return 500 Internal Server Error
        # In production, you'd log more details and possibly send alerts
        print(f"❌ Unexpected error: {str(e)}")  # CloudWatch logging
        
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }

def handle_health(event, cors_headers):
    """
    Health Check Endpoint Handler
    ============================
    
    Simple endpoint to verify the Lambda function is working.
    Used for:
    - API Gateway testing
    - Monitoring systems
    - Load balancer health checks
    - Debugging connectivity
    
    Returns basic system information and timestamp.
    """
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': 'Lambda backend is running successfully!',
            'python_version': '3.11',
            'service': 'aws-gateway-backend'
        })
    }

def handle_items(event, http_method, cors_headers):
    """
    Items Collection Handler
    =======================
    
    Handles operations on the entire collection of items:
    - GET /items: Retrieve all items (with optional filtering)
    - POST /items: Create a new item
    
    This follows REST API conventions:
    - Collection URLs (without ID) operate on multiple resources
    - Use appropriate HTTP methods for different operations
    """
    
    if http_method == 'GET':
        # ======================================================================
        # GET /items - Retrieve All Items
        # ======================================================================
        # Optional query parameter filtering: /items?category=electronics
        query_params = event.get('queryStringParameters') or {}
        category_filter = query_params.get('category')
        
        # Start with all items from storage
        filtered_items = list(items_storage.values())
        
        # Apply category filter if provided
        if category_filter:
            filtered_items = [
                item for item in filtered_items 
                if item.get('category') == category_filter
            ]
            print(f"🔍 Filtered by category '{category_filter}': {len(filtered_items)} items")
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'items': filtered_items,
                'total': len(filtered_items),
                'filter': category_filter,
                'message': f'Retrieved {len(filtered_items)} items'
            })
        }
    
    elif http_method == 'POST':
        # ======================================================================
        # POST /items - Create New Item
        # ======================================================================
        try:
            # Parse JSON body from request
            # API Gateway provides body as string, we need to parse it
            body = json.loads(event.get('body', '{}'))
            print(f"📥 Creating item with data: {body}")
            
            # ==========================================
            # INPUT VALIDATION
            # ==========================================
            # Validate required fields before processing
            if not body.get('name'):
                return {
                    'statusCode': 400,  # Bad Request
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'Name is required',
                        'field': 'name'
                    })
                }
            
            # ==========================================
            # ITEM CREATION
            # ==========================================
            # Generate unique ID for the new item
            item_id = str(uuid.uuid4())  # e.g., "123e4567-e89b-12d3-a456-426614174000"
            
            # Create item object with all fields
            new_item = {
                'id': item_id,
                'name': body['name'],
                'description': body.get('description', ''),  # Optional field
                'category': body.get('category', 'general'), # Default category
                'price': body.get('price', 0),               # Default price
                'created_at': datetime.now().isoformat(),    # ISO timestamp
                'updated_at': datetime.now().isoformat()     # Same as created for new items
            }
            
            # Store in memory (in production: save to DynamoDB)
            items_storage[item_id] = new_item
            
            print(f"✅ Created item with ID: {item_id}")
            
            return {
                'statusCode': 201,  # Created
                'headers': cors_headers,
                'body': json.dumps({
                    'item': new_item,
                    'message': 'Item created successfully'
                })
            }
            
        except json.JSONDecodeError:
            # Handle invalid JSON in request body
            return {
                'statusCode': 400,  # Bad Request
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Invalid JSON in request body',
                    'tip': 'Ensure request Content-Type is application/json'
                })
            }
    
    else:
        # Method not allowed for this endpoint
        return {
            'statusCode': 405,  # Method Not Allowed
            'headers': cors_headers,
            'body': json.dumps({
                'error': f'Method {http_method} not allowed for /items',
                'allowed_methods': ['GET', 'POST']
            })
        }

def handle_single_item(event, http_method, item_id, cors_headers):
    """
    Single Item Handler
    ==================
    
    Handles operations on individual items:
    - GET /items/{id}: Retrieve specific item
    - PUT /items/{id}: Update specific item
    - DELETE /items/{id}: Delete specific item
    
    REST Conventions:
    - Resource URLs (with ID) operate on single resources
    - PUT for complete resource updates
    - DELETE for resource removal
    """
    
    if http_method == 'GET':
        # ======================================================================
        # GET /items/{id} - Retrieve Single Item
        # ======================================================================
        if item_id not in items_storage:
            return {
                'statusCode': 404,  # Not Found
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Item not found',
                    'item_id': item_id
                })
            }
        
        item = items_storage[item_id]
        print(f"📖 Retrieved item: {item_id}")
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'item': item,
                'message': 'Item retrieved successfully'
            })
        }
    
    elif http_method == 'PUT':
        # ======================================================================
        # PUT /items/{id} - Update Item
        # ======================================================================
        try:
            body = json.loads(event.get('body', '{}'))
            print(f"📝 Updating item {item_id} with: {body}")
            
            # Check if item exists
            if item_id not in items_storage:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'Item not found',
                        'item_id': item_id
                    })
                }
            
            # ==========================================
            # UPDATE LOGIC
            # ==========================================
            # Get existing item and update fields
            existing_item = items_storage[item_id]
            
            # Update fields (keeping existing values if not provided)
            existing_item.update({
                'name': body.get('name', existing_item['name']),
                'description': body.get('description', existing_item['description']),
                'category': body.get('category', existing_item['category']),
                'price': body.get('price', existing_item['price']),
                'updated_at': datetime.now().isoformat()  # Always update timestamp
            })
            
            print(f"✅ Updated item: {item_id}")
            
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'item': existing_item,
                    'message': 'Item updated successfully'
                })
            }
            
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
    
    elif http_method == 'DELETE':
        # ======================================================================
        # DELETE /items/{id} - Delete Item
        # ======================================================================
        if item_id not in items_storage:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Item not found',
                    'item_id': item_id
                })
            }
        
        # Remove item from storage and return the deleted item
        deleted_item = items_storage.pop(item_id)
        print(f"🗑️ Deleted item: {item_id}")
        
        return {
            'statusCode': 200,  # Some APIs use 204 No Content
            'headers': cors_headers,
            'body': json.dumps({
                'item': deleted_item,
                'message': 'Item deleted successfully'
            })
        }
    
    else:
        # Method not allowed for this endpoint
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({
                'error': f'Method {http_method} not allowed for /items/{item_id}',
                'allowed_methods': ['GET', 'PUT', 'DELETE']
            })
        }

# ==============================================================================
# LAMBDA EXECUTION CONTEXT
# ==============================================================================
"""
Lambda Execution Model:
----------------------

1. COLD START: First invocation or after idle period
   - AWS creates new container
   - Loads your code
   - Executes global code (imports, global variables)
   - Calls lambda_handler()
   
2. WARM START: Subsequent invocations
   - Reuses existing container
   - Global variables persist (like items_storage)
   - Only calls lambda_handler()
   
3. SCALING: 
   - AWS automatically creates multiple containers for concurrent requests
   - Each container handles one request at a time
   - Global state is NOT shared between containers

Memory & CPU:
- Allocated memory: 128MB to 10GB
- CPU scales proportionally to memory
- More memory = faster execution (for CPU-intensive tasks)

Timeouts:
- Maximum execution time: 15 minutes
- API Gateway timeout: 30 seconds (our bottleneck)
- Configure based on expected processing time

Cost Model:
- Pay per request + execution time
- Free tier: 1M requests + 400,000 GB-seconds per month
- Very cost-effective for variable workloads

Monitoring:
- All print() statements go to CloudWatch Logs
- Automatic metrics: invocations, duration, errors
- X-Ray tracing available for debugging
"""