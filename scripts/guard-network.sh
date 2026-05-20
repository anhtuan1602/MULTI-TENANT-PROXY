#!/bin/bash
INPUT=$(cat)
if echo "$INPUT" | grep -qE "netstat|iptables|pkill"; then
    echo '{"hookSpecificOutput":{"permissionDecision":"reject","permissionDecisionReason":"Copilot blocked: Networking utilities alterations forbidden via sandbox security."}}'
    exit 0
fi
echo '{"continue":true}'
