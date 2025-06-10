#!/usr/bin/env python3
"""
Simple HTTP server for the Task Dashboard
Runs on port 8081 to avoid conflicts with other services on port 8080
Includes admin API endpoints for task management
"""

import http.server
import socketserver
import webbrowser
import os
import json
import urllib.parse
from pathlib import Path

# Use PORT environment variable if available (for Cloud Run), otherwise default to 8081
PORT = int(os.environ.get('PORT', 8081))
CONFIG_FILE = "tasks-config.json"

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for admin operations"""
        if self.path == '/api/tasks':
            self.handle_add_task()
        else:
            super().do_POST()

    def do_PUT(self):
        """Handle PUT requests for admin operations"""
        if self.path.startswith('/api/tasks/'):
            self.handle_update_task()
        else:
            self.send_error(404)

    def do_DELETE(self):
        """Handle DELETE requests for admin operations"""
        if self.path.startswith('/api/tasks/'):
            self.handle_delete_task()
        else:
            self.send_error(404)

    def do_GET(self):
        """Handle GET requests including admin endpoints"""
        if self.path == '/api/tasks':
            self.handle_get_all_tasks()
        else:
            super().do_GET()

    def load_config(self):
        """Load the tasks configuration from JSON file"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"categories": {}}
        except json.JSONDecodeError:
            return {"categories": {}}

    def save_config(self, config):
        """Save the tasks configuration to JSON file"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def send_json_response(self, data, status=200):
        """Send a JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def get_request_body(self):
        """Get and parse the request body as JSON"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {}
            
            body = self.rfile.read(content_length).decode('utf-8')
            return json.loads(body)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing request body: {e}")
            return {}

    def handle_get_all_tasks(self):
        """Get all tasks in a flat structure for admin table"""
        config = self.load_config()
        tasks = []
        
        for category_name, category_data in config.get("categories", {}).items():
            category_color = category_data.get("color", "#666666")
            for task in category_data.get("tasks", []):
                task_with_category = task.copy()
                task_with_category["category"] = category_name
                task_with_category["categoryColor"] = category_color
                tasks.append(task_with_category)
        
        self.send_json_response({"tasks": tasks})

    def handle_add_task(self):
        """Add a new task"""
        data = self.get_request_body()
        
        required_fields = ["title", "description", "priority", "category"]
        if not all(field in data for field in required_fields):
            self.send_json_response({"error": "Missing required fields"}, 400)
            return

        config = self.load_config()
        
        # Ensure category exists
        category = data["category"]
        if category not in config.get("categories", {}):
            self.send_json_response({"error": "Category does not exist"}, 400)
            return

        # Generate new ID
        all_ids = []
        for cat_data in config.get("categories", {}).values():
            for task in cat_data.get("tasks", []):
                all_ids.append(task.get("id", 0))
        
        new_id = max(all_ids, default=0) + 1

        # Create new task
        new_task = {
            "id": new_id,
            "title": data["title"],
            "description": data["description"],
            "priority": data["priority"],
            "status": data.get("status", "Open")
        }

        # Add task to category
        config["categories"][category]["tasks"].append(new_task)

        if self.save_config(config):
            self.send_json_response({"success": True, "task": new_task}, 201)
        else:
            self.send_json_response({"error": "Failed to save task"}, 500)

    def handle_update_task(self):
        """Update an existing task"""
        # Extract task ID from URL
        path_parts = self.path.split('/')
        if len(path_parts) < 4:
            self.send_json_response({"error": "Invalid task ID"}, 400)
            return
        
        try:
            task_id = int(path_parts[3])
        except ValueError:
            self.send_json_response({"error": "Invalid task ID"}, 400)
            return

        data = self.get_request_body()
        config = self.load_config()

        # Find and update task
        task_found = False
        for category_name, category_data in config.get("categories", {}).items():
            for i, task in enumerate(category_data.get("tasks", [])):
                if task.get("id") == task_id:
                    # Update task fields
                    if "title" in data:
                        task["title"] = data["title"]
                    if "description" in data:
                        task["description"] = data["description"]
                    if "priority" in data:
                        task["priority"] = data["priority"]
                    if "status" in data:
                        task["status"] = data["status"]
                    
                    # Handle category change
                    if "category" in data and data["category"] != category_name:
                        new_category = data["category"]
                        if new_category in config["categories"]:
                            # Remove from old category
                            category_data["tasks"].pop(i)
                            # Add to new category
                            config["categories"][new_category]["tasks"].append(task)
                    
                    task_found = True
                    break
            if task_found:
                break

        if not task_found:
            self.send_json_response({"error": "Task not found"}, 404)
            return

        if self.save_config(config):
            self.send_json_response({"success": True})
        else:
            self.send_json_response({"error": "Failed to save task"}, 500)

    def handle_delete_task(self):
        """Delete a task"""
        # Extract task ID from URL
        path_parts = self.path.split('/')
        if len(path_parts) < 4:
            self.send_json_response({"error": "Invalid task ID"}, 400)
            return
        
        try:
            task_id = int(path_parts[3])
        except ValueError:
            self.send_json_response({"error": "Invalid task ID"}, 400)
            return

        config = self.load_config()

        # Find and delete task
        task_found = False
        for category_data in config.get("categories", {}).values():
            for i, task in enumerate(category_data.get("tasks", [])):
                if task.get("id") == task_id:
                    category_data["tasks"].pop(i)
                    task_found = True
                    break
            if task_found:
                break

        if not task_found:
            self.send_json_response({"error": "Task not found"}, 404)
            return

        if self.save_config(config):
            self.send_json_response({"success": True})
        else:
            self.send_json_response({"error": "Failed to delete task"}, 500)

def main():
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        # Get the local IP address for network access
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"🚀 Task Dashboard server running at:")
        print(f"   📱 Local access: http://localhost:{PORT}")
        print(f"   🌐 Network access: http://{local_ip}:{PORT}")
        print(f"📁 Serving files from: {script_dir}")
        print("💡 To stop the server, press Ctrl+C")
        print()
        print("📝 To edit tasks, modify the 'tasks-config.json' file")
        print("🔄 The dashboard will automatically refresh every 60 seconds")
        print("🔧 Admin interface available for managing tasks")
        print()
        print("🏠 Other devices on your network can access via:")
        print(f"   http://{local_ip}:{PORT}")
        
        # Only try to open browser in local development
        if os.environ.get('PORT') is None:  # Local development
            try:
                webbrowser.open(f'http://localhost:{PORT}')
            except:
                pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main() 