# Task Dashboard

A beautiful, modern web dashboard for displaying categorized tasks to your husband. Features a clean interface with color-coded categories, priority levels, and due dates.

## Features

- 📋 **Categorized Tasks**: Organize tasks by categories (Household, Maintenance, Shopping, etc.)
- 🎨 **Color-Coded Categories**: Each category has its own color for easy identification
- 📅 **Due Dates**: Smart date formatting shows "Today", "Tomorrow", or relative dates
- ⚡ **Priority Levels**: High, Medium, and Low priority badges
- 📱 **Responsive Design**: Works great on desktop, tablet, and mobile
- 🔄 **Auto-Refresh**: Dashboard updates every 30 seconds automatically
- ⚙️ **Easy Configuration**: Simple JSON file to manage all tasks

## Quick Start

### Option 1: Using Python Server (Recommended)

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Open your browser** - it should automatically open to `http://localhost:8080`

### Option 2: Using Built-in Python HTTP Server

```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

### Option 3: Using Node.js (if you have it)

```bash
npx http-server -p 8080
```

## Managing Tasks

Edit the `tasks-config.json` file to add, remove, or modify tasks:

```json
{
  "categories": {
    "Category Name": {
      "color": "#4CAF50",
      "tasks": [
        {
          "id": 1,
          "title": "Task Title",
          "description": "Detailed description of the task",
          "priority": "high",
          "dueDate": "2024-01-25"
        }
      ]
    }
  }
}
```

### Task Properties

- **id**: Unique identifier for the task
- **title**: Short, descriptive title
- **description**: Detailed explanation of what needs to be done
- **priority**: `"high"`, `"medium"`, or `"low"`
- **dueDate**: Date in YYYY-MM-DD format

### Category Properties

- **color**: Hex color code for the category (e.g., "#4CAF50")
- **tasks**: Array of task objects

## Color Suggestions

- 🟢 Green: `#4CAF50` (Household/Routine)
- 🟠 Orange: `#FF9800` (Maintenance/Repairs)
- 🔵 Blue: `#2196F3` (Shopping/Errands)
- 🟣 Purple: `#9C27B0` (Personal/Health)
- 🔴 Red: `#F44336` (Urgent/Important)
- 🟡 Yellow: `#FFEB3B` (Work/Projects)

## File Structure

```
task-dashboard/
├── index.html          # Main dashboard page
├── tasks-config.json   # Task configuration file
├── server.py           # Python server script
└── README.md           # This file
```

## Tips

1. **Keep descriptions concise** but informative
2. **Use consistent due dates** for better organization
3. **Regular updates**: Edit the JSON file as tasks are completed
4. **Categories**: Create categories that make sense for your household
5. **Priority levels**: Use consistently to help prioritize work

## Troubleshooting

### Dashboard shows "Unable to load tasks"
- Make sure you're running a local server (not just opening the HTML file)
- Check that `tasks-config.json` is in the same directory as `index.html`
- Verify the JSON syntax is valid

### Server won't start on port 8080
- Check if another application is using port 8080
- Try a different port by modifying `server.py`
- Use `netstat -an | findstr 8080` (Windows) to check port usage

### Browser doesn't auto-open
- Manually navigate to `http://localhost:8080`
- Check firewall settings if accessing from another device

## Customization

The dashboard is fully customizable:
- Modify CSS in `index.html` for different colors/styling
- Add new task properties by editing the JavaScript
- Change refresh interval by modifying the `setInterval` value
- Add new categories by editing `tasks-config.json` 