#!/usr/bin/env bash
# Util command to run tests and code lint.

pytest && isort click_web tests && flake8 click_web tests
retVal=$?
if [ $retVal -eq 0 ]; then
    echo "All checks OK!"
else
    echo "Check failed, please fix above errors."

fi
exit
