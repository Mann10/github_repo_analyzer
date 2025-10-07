from http.server import HTTPServer
from github_repo_analyzer.server import app
from mcp.server import Server
import json
from http import HTTPStatus
import asyncio
import os

async def handle_request(request_body):
    try:
        data = json.loads(request_body)
        tool_name = data.get('tool')
        args = data.get('args', {})
        
        # Initialize server
        server = Server(app)
        
        # Call the tool
        result = await server.call_tool(tool_name, args)
        return {'result': result}, HTTPStatus.OK
        
    except Exception as e:
        return {'error': str(e)}, HTTPStatus.BAD_REQUEST

def handler(event, context):
    # Parse request body
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)
    
    # Run the async handler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response, status_code = loop.run_until_complete(handle_request(body))
    loop.close()
    
    # Return response
    return {
        'statusCode': status_code,
        'body': json.dumps(response),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    }