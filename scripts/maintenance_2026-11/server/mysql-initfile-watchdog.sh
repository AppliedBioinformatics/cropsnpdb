#!/bin/bash
# CropSNPdb: the mysql-server-8.0 postinst (run_init_sql) starts a temporary `mysqld --init-file=...` that never
# exits on this server, so package updates hang and apt is blocked. Stop any such mysqld running > 10 min
# (clean SIGTERM); the postinst then finishes and starts the normal mysql service.
# Only processes whose executable name is exactly mysqld are considered.
for pid in $(pgrep -x mysqld); do
  ps -o args= -p "$pid" | grep -q -- '--init-file=' || continue
  age=$(ps -o etimes= -p "$pid" | tr -d ' ')
  if [ -n "$age" ] && [ "$age" -gt 600 ]; then
    logger -t mysql-initfile-watchdog "stopping temporary mysqld --init-file pid $pid (running ${age}s)"
    kill -TERM "$pid"
  fi
done
