#!/usr/bin/env bash
# Util command to run tests and code lint.

pytest && isort && flake8
retVal=$?
if [ $retVal -eq 0 ]; then
    echo "All checks OK!"
else
    echo "Check failed, please fix above errors."

fi
exit
