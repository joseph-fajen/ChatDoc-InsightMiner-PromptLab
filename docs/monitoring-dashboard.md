# Monitoring Dashboard

The Monitoring Dashboard provides real-time visibility into your nodes and services, allowing you to track performance, detect issues, and ensure optimal operation.

## Accessing the Dashboard

You can access the monitoring dashboard at `https://dashboard.example.com` using your account credentials. Single sign-on (SSO) is also supported for enterprise customers.

## Dashboard Overview

The main dashboard screen is divided into several key sections:

- **System Overview**: High-level metrics across all your nodes
- **Active Nodes**: List of all online nodes with key status indicators
- **Alert History**: Recent alerts and notifications
- **Performance Metrics**: CPU, memory, and network graphs

## Identifying Your Nodes

Each node in your infrastructure has a unique identifier (Node ID) that appears in the monitoring dashboard. To identify your specific node:

1. Find your Node ID in your configuration file:
   - Located at `~/.config/myapp/config.yaml`
   - Look for the `node_id` field

2. In the monitoring dashboard, navigate to the "Active Nodes" section.

3. Use the search function to find your Node ID, or scroll through the list.

4. You can rename your node for easier identification:
   - Click on the node in the list
   - Select "Edit Node Details"
   - Enter a custom display name
   - Click "Save Changes"

The display name will appear alongside the Node ID in the dashboard for easier identification.

## Customizing Your View

The dashboard view can be customized to focus on the metrics most important to you:

1. Click the "Customize" button in the top-right corner
2. Drag and drop widgets to rearrange them
3. Add or remove widgets from the "Available Widgets" section
4. Click "Save Layout" when finished

Your customized layout will be saved to your user profile and maintained across sessions.

## Setting Up Alerts

You can configure alerts to be notified of important events:

1. Navigate to the "Alerts" tab
2. Click "Add Alert"
3. Select the metric to monitor (e.g., "Node Status", "CPU Usage", "Memory")
4. Configure the threshold and condition
5. Choose notification methods (Email, Webhook)
6. Click "Create Alert"

Currently, alerts can be delivered via email or webhook. SMS notifications will be available in an upcoming release.

## Troubleshooting

### Dashboard Not Loading

If the dashboard fails to load:

1. Check your internet connection
2. Clear your browser cache and cookies
3. Ensure you're using a supported browser (Chrome, Firefox, Safari, Edge)
4. Verify that your account has the necessary permissions

### Node Not Appearing

If your node doesn't appear in the dashboard:

1. Verify the node is running with `systemctl status myapp-node`
2. Check that the monitoring agent is enabled in your config file
3. Ensure your firewall allows outbound connections on port 443
4. Look for errors in the node logs: `/var/log/myapp/node.log`

### Data Not Updating

If the dashboard metrics aren't updating:

1. Check your refresh rate setting (Settings > Refresh Rate)
2. Try a hard refresh (Ctrl+F5 or Cmd+Shift+R)
3. Verify that the monitoring agent on your node is operational
4. Check for browser extensions that might block WebSocket connections

## Exporting Data

Dashboard data can be exported for further analysis:

1. Click the gear icon in the top-right corner
2. Select "Export Data"
3. Choose your preferred format (CSV, JSON, Excel)
4. Select the time range
5. Click "Export"

Exported data will include all metrics visible in your current dashboard view.