#!/bin/bash

bin/oracle-price-feed \
    --token ETH \
    --ro-account user:readonly \
    --rw-account user:readwrite \
    --fetch-time 10 \
    --report-time 2
