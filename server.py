#!/usr/bin/env python3
"""
Simple HTTP server for the Task Dashboard
Runs on port 8081 to avoid conflicts with other services on port 8080
Includes admin API endpoints for task management
Uses Google Cloud Firestore for persistent data storage
"""

import http.server
import socketserver
import webbrowser
import os
import json
import urllib.parse
from pathlib import Path

# Google Cloud Firestore
from google.cloud import firestore

# Use PORT environment variable if available (for Cloud Run), otherwise default to 8081
PORT = int(os.environ.get('PORT', 8081))
CONFIG_FILE = "tasks-config.json"  # For initial migration only

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Initialize Firestore client
        self.db = firestore.Client()
        super().__init__(*args, **kwargs)

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
        elif self.path == '/api/categories':
            self.handle_get_categories()
        elif self.path == '/api/migrate':
            self.handle_migration()
        else:
            super().do_GET()

    def get_categories_from_firestore(self):
        """Get all categories and their tasks from Firestore"""
        try:
            print("Getting categories from Firestore...")
            categories = {}
            
            # Get all categories with timeout protection
            categories_ref = self.db.collection('categories')
            category_docs = list(categories_ref.stream())
            print(f"Found {len(category_docs)} categories")
            
            # Get all tasks at once (more efficient)
            tasks_ref = self.db.collection('tasks')
            all_task_docs = list(tasks_ref.stream())
            print(f"Found {len(all_task_docs)} tasks")
            
            # Group tasks by category
            tasks_by_category = {}
            for task_doc in all_task_docs:
                task_data = task_doc.to_dict()
                task_data['id'] = int(task_doc.id)  # Ensure ID is integer
                category = task_data.get('category', 'Unknown')
                
                if category not in tasks_by_category:
                    tasks_by_category[category] = []
                tasks_by_category[category].append(task_data)
            
            # Build categories structure
            for category_doc in category_docs:
                category_data = category_doc.to_dict()
                category_name = category_doc.id
                
                # Get tasks for this category
                tasks = tasks_by_category.get(category_name, [])
                
                # Sort tasks by ID
                tasks.sort(key=lambda x: x.get('id', 0))
                
                categories[category_name] = {
                    'color': category_data.get('color', '#666666'),
                    'tasks': tasks
                }
            
            print(f"Successfully built {len(categories)} categories")
            return categories
            
        except Exception as e:
            print(f"Error getting categories from Firestore: {e}")
            # Fallback to empty structure
            return {}

    def load_config_from_json(self):
        """Load the tasks configuration from JSON file (fallback/migration)"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('categories', {})
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def migrate_json_to_firestore(self):
        """One-time migration from JSON to Firestore"""
        try:
            # Check if migration is already done
            categories_ref = self.db.collection('categories')
            existing_categories = list(categories_ref.limit(1).stream())
            
            if existing_categories:
                print("Migration already completed - Firestore has data")
                return
            
            print("Migrating data from JSON to Firestore...")
            json_data = self.load_config_from_json()
            
            if not json_data:
                print("No JSON data to migrate")
                return
            
            batch = self.db.batch()
            
            for category_name, category_data in json_data.items():
                # Create category document
                category_ref = self.db.collection('categories').document(category_name)
                batch.set(category_ref, {
                    'color': category_data.get('color', '#666666'),
                    'created_at': firestore.SERVER_TIMESTAMP
                })
                
                # Create task documents
                for task in category_data.get('tasks', []):
                    task_id = str(task.get('id', 1))
                    task_ref = self.db.collection('tasks').document(task_id)
                    task_data = {
                        'title': task.get('title', ''),
                        'description': task.get('description', ''),
                        'priority': task.get('priority', 'medium'),
                        'status': task.get('status', 'Open'),
                        'category': category_name,
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    }
                    batch.set(task_ref, task_data)
            
            # Commit the batch
            batch.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")

    def handle_get_categories(self):
        """API endpoint to get all categories with their tasks from Firestore"""
        try:
            print("Starting handle_get_categories")
            categories = self.get_categories_from_firestore()
            
            # If Firestore fails, try JSON file as fallback
            if not categories:
                print("Firestore returned empty, trying JSON fallback")
                categories = self.load_config_from_json()
            
            # If still empty, create a minimal structure to prevent errors
            if not categories:
                print("No data found, creating minimal structure")
                categories = {
                    "No Data": {
                        "color": "#666666",
                        "tasks": [{
                            "id": 1,
                            "title": "Migration needed",
                            "description": "Run /api/migrate to import your data",
                            "priority": "high",
                            "status": "Open"
                        }]
                    }
                }
            
            config = {"categories": categories}
            print(f"Serving config with {len(categories)} categories")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            self.wfile.write(json.dumps(config, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"Error serving config JSON: {e}")
            # Send a valid JSON error response instead of HTML
            try:
                self.send_response(200)  # Send 200 to avoid browser errors
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                error_config = {
                    "categories": {
                        "Error": {
                            "color": "#ff0000",
                            "tasks": [{
                                "id": 1,
                                "title": "Error loading data",
                                "description": f"Server error: {str(e)}",
                                "priority": "high",
                                "status": "Open"
                            }]
                        }
                    }
                }
                self.wfile.write(json.dumps(error_config, ensure_ascii=False).encode('utf-8'))
            except:
                self.send_error(500)

    def handle_migration(self):
        """Handle migration request via HTTP"""
        try:
            # Load JSON data first to check what we have
            json_data = self.load_config_from_json()
            
            if not json_data:
                self.send_json_response({
                    'success': False, 
                    'message': 'No JSON data found to migrate',
                    'error': 'tasks-config.json is empty or missing'
                }, 400)
                return
            
            # Check existing Firestore data
            categories_ref = self.db.collection('categories')
            existing_categories = list(categories_ref.limit(1).stream())
            
            if existing_categories:
                self.send_json_response({
                    'success': False,
                    'message': 'Migration already completed',
                    'info': 'Firestore already contains data. Delete existing data first if you want to re-migrate.'
                })
                return
            
            # Perform migration
            batch = self.db.batch()
            total_tasks = 0
            
            for category_name, category_data in json_data.items():
                # Create category document
                category_ref = self.db.collection('categories').document(category_name)
                batch.set(category_ref, {
                    'color': category_data.get('color', '#666666'),
                    'created_at': firestore.SERVER_TIMESTAMP
                })
                
                # Create task documents
                for task in category_data.get('tasks', []):
                    task_id = str(task.get('id', 1))
                    task_ref = self.db.collection('tasks').document(task_id)
                    task_data = {
                        'title': task.get('title', ''),
                        'description': task.get('description', ''),
                        'priority': task.get('priority', 'medium'),
                        'status': task.get('status', 'Open'),
                        'category': category_name,
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    }
                    batch.set(task_ref, task_data)
                    total_tasks += 1
            
            # Commit the batch
            batch.commit()
            
            self.send_json_response({
                'success': True,
                'message': 'Migration completed successfully!',
                'categories_migrated': len(json_data),
                'tasks_migrated': total_tasks
            })
            
        except Exception as e:
            print(f"Error during HTTP migration: {e}")
            self.send_json_response({
                'success': False,
                'message': 'Migration failed',
                'error': str(e)
            }, 500)

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
        try:
            tasks = []
            
            # Get all tasks from Firestore
            tasks_ref = self.db.collection('tasks')
            task_docs = tasks_ref.stream()
            
            # Get category colors
            categories = self.get_categories_from_firestore()
            
            for task_doc in task_docs:
                task_data = task_doc.to_dict()
                task_data['id'] = int(task_doc.id)
                
                # Add category color
                category_name = task_data.get('category', '')
                category_color = '#666666'
                if category_name in categories:
                    category_color = categories[category_name].get('color', '#666666')
                
                task_data['categoryColor'] = category_color
                tasks.append(task_data)
            
            # Sort by ID
            tasks.sort(key=lambda x: x.get('id', 0))
            
            self.send_json_response({"tasks": tasks})
            
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            self.send_json_response({"error": "Failed to load tasks"}, 500)

    def handle_add_task(self):
        """Add a new task"""
        try:
            data = self.get_request_body()
            
            required_fields = ["title", "description", "priority", "category"]
            if not all(field in data for field in required_fields):
                self.send_json_response({"error": "Missing required fields"}, 400)
                return

            # Check if category exists
            category = data["category"]
            category_ref = self.db.collection('categories').document(category)
            if not category_ref.get().exists:
                self.send_json_response({"error": "Category does not exist"}, 400)
                return

            # Generate new ID
            tasks_ref = self.db.collection('tasks')
            all_tasks = tasks_ref.stream()
            max_id = 0
            for task_doc in all_tasks:
                try:
                    task_id = int(task_doc.id)
                    max_id = max(max_id, task_id)
                except ValueError:
                    continue
            
            new_id = max_id + 1

            # Create new task
            new_task_data = {
                "title": data["title"],
                "description": data["description"],
                "priority": data["priority"],
                "status": data.get("status", "Open"),
                "category": category,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            }

            # Save to Firestore
            task_ref = self.db.collection('tasks').document(str(new_id))
            task_ref.set(new_task_data)

            # Return the created task
            new_task_data['id'] = new_id
            self.send_json_response({"success": True, "task": new_task_data}, 201)

        except Exception as e:
            print(f"Error adding task: {e}")
            self.send_json_response({"error": "Failed to add task"}, 500)

    def handle_update_task(self):
        """Update an existing task"""
        try:
            # Extract task ID from URL
            path_parts = self.path.split('/')
            if len(path_parts) < 4:
                self.send_json_response({"error": "Invalid task ID"}, 400)
                return
            
            try:
                task_id = str(int(path_parts[3]))  # Ensure it's a valid integer
            except ValueError:
                self.send_json_response({"error": "Invalid task ID"}, 400)
                return

            data = self.get_request_body()
            
            # Get task reference
            task_ref = self.db.collection('tasks').document(task_id)
            task_doc = task_ref.get()
            
            if not task_doc.exists:
                self.send_json_response({"error": "Task not found"}, 404)
                return

            # Update task data
            update_data = {"updated_at": firestore.SERVER_TIMESTAMP}
            
            if "title" in data:
                update_data["title"] = data["title"]
            if "description" in data:
                update_data["description"] = data["description"]
            if "priority" in data:
                update_data["priority"] = data["priority"]
            if "status" in data:
                update_data["status"] = data["status"]
            if "category" in data:
                # Verify new category exists
                category_ref = self.db.collection('categories').document(data["category"])
                if category_ref.get().exists:
                    update_data["category"] = data["category"]

            # Update in Firestore
            task_ref.update(update_data)
            
            self.send_json_response({"success": True})

        except Exception as e:
            print(f"Error updating task: {e}")
            self.send_json_response({"error": "Failed to update task"}, 500)

    def handle_delete_task(self):
        """Delete a task"""
        try:
            # Extract task ID from URL
            path_parts = self.path.split('/')
            if len(path_parts) < 4:
                self.send_json_response({"error": "Invalid task ID"}, 400)
                return
            
            try:
                task_id = str(int(path_parts[3]))  # Ensure it's a valid integer
            except ValueError:
                self.send_json_response({"error": "Invalid task ID"}, 400)
                return

            # Get task reference
            task_ref = self.db.collection('tasks').document(task_id)
            task_doc = task_ref.get()
            
            if not task_doc.exists:
                self.send_json_response({"error": "Task not found"}, 404)
                return

            # Delete from Firestore
            task_ref.delete()
            
            self.send_json_response({"success": True})

        except Exception as e:
            print(f"Error deleting task: {e}")
            self.send_json_response({"error": "Failed to delete task"}, 500)

def main():
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Initialize handler and migrate data
    print("🔥 Initializing Firestore connection...")
    
    try:
        # Create a temporary handler instance to perform migration
        db = firestore.Client()
        
        # Check if migration is needed
        categories_ref = db.collection('categories')
        existing_categories = list(categories_ref.limit(1).stream())
        
        if not existing_categories:
            print("🚀 Performing one-time migration from JSON to Firestore...")
            temp_handler = Handler(None, None, None)
            temp_handler.migrate_json_to_firestore()
        else:
            print("✅ Firestore already contains data")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Firestore: {e}")
        print("📝 Make sure you're authenticated with Google Cloud")
    
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
        print("🔥 Using Google Cloud Firestore for persistent data storage")
        print("📝 Tasks will persist across deployments and server restarts")
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