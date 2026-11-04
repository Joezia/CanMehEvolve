#!/bin/sh
# Compiler wrapper for C1 `-O3 -march=native`: CanMehHarness passes --opt as ONE
# compiler argument, so a second flag has to come in through --cxx.
exec c++ -march=native "$@"
