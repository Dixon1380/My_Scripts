#!/bin/bash
echo "🚀 Deploying AI Blog Scripts to Host..."
cd /home/dabiddo/projects/My_Scripts/Automation_Ai_Scripts/ai_blog_scripts
scp -r * dabiddo@192.168.8.234:/home/dabiddo/docker/ai-task-runner/scripts
echo "✅ Deployment Completed!"