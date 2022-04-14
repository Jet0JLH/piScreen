#!/bin/bash
browser=firefox-esr
processID=$(pgrep -x $browser)
kill $processID