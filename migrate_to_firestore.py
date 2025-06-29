#!/usr/bin/env python3
"""
Migration script to import tasks-config.json data into Firestore
Run this locally to populate your Firestore database with all your existing tasks
"""

import json
from google.cloud import firestore

def migrate_json_to_firestore():
    """Migrate data from tasks-config.json to Firestore"""
    
    # Initialize Firestore client
    print("🔥 Connecting to Firestore...")
    db = firestore.Client()
    
    # Load JSON data
    print("📖 Reading tasks-config.json...")
    try:
        with open('tasks-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Error: tasks-config.json file not found!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format: {e}")
        return
    
    categories_data = config.get('categories', {})
    
    if not categories_data:
        print("❌ No categories found in JSON file!")
        return
    
    print(f"✅ Found {len(categories_data)} categories")
    
    # Count existing data
    existing_categories = list(db.collection('categories').limit(1).stream())
    existing_tasks = list(db.collection('tasks').limit(1).stream())
    
    if existing_categories or existing_tasks:
        print("⚠️  Firestore already contains data!")
        response = input("Do you want to add to existing data? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Migration cancelled")
            return
    
    # Start migration
    print("🚀 Starting migration...")
    
    # Create batch for efficient writes
    batch = db.batch()
    batch_count = 0
    
    total_tasks = 0
    
    for category_name, category_data in categories_data.items():
        print(f"📂 Processing category: {category_name}")
        
        # Create/update category document
        category_ref = db.collection('categories').document(category_name)
        batch.set(category_ref, {
            'color': category_data.get('color', '#666666'),
            'created_at': firestore.SERVER_TIMESTAMP
        }, merge=True)  # merge=True to avoid overwriting existing data
        
        batch_count += 1
        
        # Process tasks for this category
        tasks = category_data.get('tasks', [])
        print(f"   📝 Found {len(tasks)} tasks")
        
        for task in tasks:
            task_id = str(task.get('id', 1))
            task_ref = db.collection('tasks').document(task_id)
            
            task_data = {
                'title': task.get('title', ''),
                'description': task.get('description', ''),
                'priority': task.get('priority', 'medium'),
                'status': task.get('status', 'Open'),
                'category': category_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            batch.set(task_ref, task_data, merge=True)  # merge=True to avoid overwriting
            batch_count += 1
            total_tasks += 1
            
            # Commit batch every 500 operations (Firestore limit)
            if batch_count >= 400:
                print(f"   💾 Committing batch ({batch_count} operations)...")
                batch.commit()
                batch = db.batch()
                batch_count = 0
    
    # Commit final batch
    if batch_count > 0:
        print(f"💾 Committing final batch ({batch_count} operations)...")
        batch.commit()
    
    print(f"🎉 Migration completed successfully!")
    print(f"   📂 Categories: {len(categories_data)}")
    print(f"   📝 Tasks: {total_tasks}")
    print("\n🧪 Test your app now - all data should be visible!")

def verify_migration():
    """Verify the migration by checking Firestore data"""
    print("\n🔍 Verifying migration...")
    
    db = firestore.Client()
    
    # Check categories
    categories = list(db.collection('categories').stream())
    print(f"✅ Categories in Firestore: {len(categories)}")
    for cat in categories:
        print(f"   📂 {cat.id}: {cat.to_dict().get('color', 'No color')}")
    
    # Check tasks
    tasks = list(db.collection('tasks').stream())
    print(f"✅ Tasks in Firestore: {len(tasks)}")
    
    # Group by category
    tasks_by_category = {}
    for task in tasks:
        task_data = task.to_dict()
        category = task_data.get('category', 'Unknown')
        if category not in tasks_by_category:
            tasks_by_category[category] = 0
        tasks_by_category[category] += 1
    
    for category, count in tasks_by_category.items():
        print(f"   📝 {category}: {count} tasks")

if __name__ == "__main__":
    print("🔄 Firestore Migration Tool")
    print("=" * 50)
    
    try:
        migrate_json_to_firestore()
        verify_migration()
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("Make sure you're authenticated with Google Cloud and in the right project") 