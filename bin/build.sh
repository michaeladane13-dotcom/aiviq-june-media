#!/bin/bash
# Build + stably sign the Reminders helper. Re-run after editing add_reminder.swift.
# The stable signing identity (com.aiviq.addreminder) is what TCC keys the
# Reminders permission to, so the one-time "Allow" grant survives rebuilds.
set -e
cd "$(dirname "$0")"
swiftc -O add_reminder.swift -o add_reminder
codesign -s - -i com.aiviq.addreminder --force add_reminder
echo "Built + signed bin/add_reminder ($(codesign -dvv add_reminder 2>&1 | grep -i '^Identifier='))"
