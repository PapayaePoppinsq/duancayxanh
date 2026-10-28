import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.join(current_dir, 'code')
if code_dir not in sys.path:
    sys.path.insert(0, code_dir)

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
