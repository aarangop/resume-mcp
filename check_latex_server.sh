#!/bin/bash
# Simple script to check LaTeX server status and provide helpful information

echo "🔍 Checking LaTeX compilation server status..."

# Try to connect to the server
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7474/health 2>/dev/null)

if [ "$response" = "200" ]; then
  echo "✅ LaTeX server is running!"
  echo "Full server status:"
  curl -s http://localhost:7474/health | python3 -m json.tool
else
  echo "❌ LaTeX server is not running or not responding"
  echo "Would you like to start the server? (y/n)"
  read -r answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Starting LaTeX server..."
    cd latex-compilation-server || { echo "Error: latex-compilation-server directory not found"; exit 1; }
    docker-compose up -d
    echo "Waiting for server to start..."
    sleep 5
    
    # Check again
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7474/health 2>/dev/null)
    if [ "$response" = "200" ]; then
      echo "✅ LaTeX server started successfully!"
    else
      echo "⚠️ LaTeX server may not have started correctly. Check logs with:"
      echo "cd latex-compilation-server && docker-compose logs"
    fi
  fi
fi

echo -e "\n💡 Quick Reference:"
echo "- Start server:   cd latex-compilation-server && docker-compose up -d"
echo "- Stop server:    cd latex-compilation-server && docker-compose down"
echo "- Server logs:    cd latex-compilation-server && docker-compose logs -f"
echo "- Test endpoint:  curl http://localhost:7474/health"
