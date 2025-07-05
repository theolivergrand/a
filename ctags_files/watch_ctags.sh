#!/bin/bash

# Auto-update ctags when Python files change
# Requires inotify-tools: sudo apt-get install inotify-tools

WATCH_DIR="/workspaces/a"
TAGS_FILE="$WATCH_DIR/tags"

echo "👀 Watching for Python file changes in $WATCH_DIR"
echo "📋 Will auto-update $TAGS_FILE"

# Function to update tags
update_tags() {
    echo "🔄 File changed: $1"
    echo "📝 Updating ctags..."
    cd "$WATCH_DIR"
    ctags -R --fields=+iaS --extras=+q --output-format=e-ctags . 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Tags updated successfully"
        TAG_COUNT=$(wc -l < tags)
        echo "📊 Total tags: $TAG_COUNT"
    else
        echo "❌ Failed to update tags"
    fi
    echo "---"
}

# Check if inotify-tools is installed
if ! command -v inotifywait &> /dev/null; then
    echo "❌ inotifywait not found. Install with:"
    echo "   sudo apt-get install inotify-tools"
    exit 1
fi

# Initial tag generation
echo "🚀 Generating initial tags..."
update_tags "initial"

# Watch for changes
inotifywait -m -r -e modify,create,delete,move \
    --include='\.py$' \
    "$WATCH_DIR" |
while read -r directory events filename; do
    # Avoid infinite loops by excluding the tags file itself
    if [[ "$filename" != "tags" ]]; then
        update_tags "$directory$filename"
    fi
done
