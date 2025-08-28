import json
import boto3
from datetime import datetime
import uuid

# In-memory storage for demo (in production, use DynamoDB)
items_storage = {}

def lambda_handler(event, context):
    """
    Main Lambda handler for all HTTP methods
    """
    try:
        # Extract HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # CORS headers for all responses
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        }
        
        # Handle OPTIONS request for CORS preflight
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }
        
        # Route to appropriate handler
        if path == '/health':
            return handle_health(event, cors_headers)
        elif path == '/items':
            return handle_items(event, http_method, cors_headers)
        elif path.startswith('/items/'):
            item_id = path.split('/')[-1]
            return handle_single_item(event, http_method, item_id, cors_headers)
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Path not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }

def handle_health(event, cors_headers):
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': 'Lambda backend is running successfully!'
        })
    }

def handle_items(event, http_method, cors_headers):
    """Handle /items endpoint"""
    
    if http_method == 'GET':
        # Get all items with optional filtering
        query_params = event.get('queryStringParameters') or {}
        category_filter = query_params.get('category')
        
        filtered_items = list(items_storage.values())
        if category_filter:
            filtered_items = [item for item in filtered_items if item.get('category') == category_filter]
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'items': filtered_items,
                'total': len(filtered_items),
                'message': f'Retrieved {len(filtered_items)} items'
            })
        }
    
    elif http_method == 'POST':
        # Create new item
        try:
            body = json.loads(event.get('body', '{}'))
            
            # Validate required fields
            if not body.get('name'):
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Name is required'})
                }
            
            # Create new item
            item_id = str(uuid.uuid4())
            new_item = {
                'id': item_id,
                'name': body['name'],
                'description': body.get('description', ''),
                'category': body.get('category', 'general'),
                'price': body.get('price', 0),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            items_storage[item_id] = new_item
            
            return {
                'statusCode': 201,
                'headers': cors_headers,
                'body': json.dumps({
                    'item': new_item,
                    'message': 'Item created successfully'
                })
            }
            
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
    
    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': f'Method {http_method} not allowed for /items'})
        }

def handle_single_item(event, http_method, item_id, cors_headers):
    """Handle /items/{id} endpoint"""
    
    if http_method == 'GET':
        # Get single item
        if item_id not in items_storage:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Item not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'item': items_storage[item_id],
                'message': 'Item retrieved successfully'
            })
        }
    
    elif http_method == 'PUT':
        # Update item
        try:
            body = json.loads(event.get('body', '{}'))
            
            if item_id not in items_storage:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Item not found'})
                }
            
            # Update item
            existing_item = items_storage[item_id]
            existing_item.update({
                'name': body.get('name', existing_item['name']),
                'description': body.get('description', existing_item['description']),
                'category': body.get('category', existing_item['category']),
                'price': body.get('price', existing_item['price']),
                'updated_at': datetime.now().isoformat()
            })
            
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
        # Delete item
        if item_id not in items_storage:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Item not found'})
            }
        
        deleted_item = items_storage.pop(item_id)
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'item': deleted_item,
                'message': 'Item deleted successfully'
            })
        }
    
    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': f'Method {http_method} not allowed for /items/{item_id}'})
        }