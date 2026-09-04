import uvicorn
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == '__main__':
    print('Starting SIH26034 Pre-Packed Commodity Inspection Server...')
    print('Access Swagger UI Docs at: http://127.0.0.1:8000/docs')
    print('Access Web Dashboard at:  http://127.0.0.1:8000')
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
