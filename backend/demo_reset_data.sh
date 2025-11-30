#!/bin/bash
# ============================================================================
# Reset demo data to known good state
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKUP_FILE="data/demo_backup/demo_data.sql"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "[ERROR] Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Resetting demo data..."
echo "[1/3] Clearing existing data..."

PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db << EOF
TRUNCATE TABLE evidence CASCADE;
TRUNCATE TABLE skill_assessments CASCADE;
TRUNCATE TABLE behavioral_features CASCADE;
TRUNCATE TABLE linguistic_features CASCADE;
TRUNCATE TABLE transcripts CASCADE;
TRUNCATE TABLE students CASCADE;
TRUNCATE TABLE schools CASCADE;
TRUNCATE TABLE users CASCADE;
EOF

echo "[2/3] Restoring demo data..."
PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db < "$BACKUP_FILE"

echo "[3/3] Verifying..."
STUDENT_COUNT=$(PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -t -c "SELECT COUNT(*) FROM students" | tr -d ' ')
ASSESSMENT_COUNT=$(PGPASSWORD=mass_password psql -h 127.0.0.1 -p 5432 -U mass_user -d mass_db -t -c "SELECT COUNT(*) FROM skill_assessments" | tr -d ' ')

echo ""
echo "Demo data restored:"
echo "  Students: $STUDENT_COUNT"
echo "  Assessments: $ASSESSMENT_COUNT"
echo ""
echo "Done!"
