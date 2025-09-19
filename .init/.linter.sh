#!/bin/bash
cd /home/kavia/workspace/code-generation/kavia-ai-crm-platform-87080-87094/crm_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

