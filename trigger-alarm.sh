#!/bin/sh

#pid=`ps aux | grep test_sig.py | grep -v grep | awk '{print $2}'`
pid=`ps aux | grep alarm-blinds.py | grep -v grep | awk '{print $2}'`
kill -s 10 $pid #SIGUSR1=10
