#!/bin/bash

gcc -Wall -O3 ThreadsSync.c -o ThreadsSync -lpthread
./ThreadsSync
