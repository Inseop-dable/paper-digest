#!/bin/bash
# Paper Digest Cron Job Setup
# Usage: ./scripts/setup-cron.sh [HOUR] [MINUTE]
# Example: ./scripts/setup-cron.sh 9 0  -> Run daily at 9:00 AM

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RUN_SCRIPT="${SCRIPT_DIR}/run.sh"
LOG_FILE="${PROJECT_ROOT}/output/cron.log"

# Default: 9:00 AM
HOUR="${1:-9}"
MINUTE="${2:-0}"

# Validate input
if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
    echo "Error: HOUR must be 0-23"
    exit 1
fi

if ! [[ "$MINUTE" =~ ^[0-9]+$ ]] || [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
    echo "Error: MINUTE must be 0-59"
    exit 1
fi

# Ensure run script is executable
chmod +x "$RUN_SCRIPT"

# Build cron command
# Use full paths and ensure environment is set up
CRON_CMD="$MINUTE $HOUR * * * cd $PROJECT_ROOT && $RUN_SCRIPT >> $LOG_FILE 2>&1"

echo "=== Paper Digest Cron Job Setup ==="
echo ""
echo "Schedule: Daily at ${HOUR}:$(printf '%02d' $MINUTE)"
echo ""
echo "Cron entry:"
echo "  $CRON_CMD"
echo ""

# Ask for confirmation
read -p "Add this cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove existing paper-digest cron entries and add new one
    (crontab -l 2>/dev/null | grep -v "paper-digest" | grep -v "$PROJECT_ROOT"; echo "$CRON_CMD") | crontab -

    echo ""
    echo "Cron job added successfully!"
    echo ""
    echo "Current cron jobs:"
    crontab -l 2>/dev/null | grep -E "(paper-digest|$PROJECT_ROOT)" || echo "  (none found - this is unexpected)"
    echo ""
    echo "Logs will be written to: $LOG_FILE"
else
    echo ""
    echo "Cancelled."
    echo ""
    echo "To add manually, run:"
    echo "  crontab -e"
    echo ""
    echo "Then add this line:"
    echo "  $CRON_CMD"
fi
