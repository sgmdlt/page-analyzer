#!/usr/bin/env bash

sleep 5 && psql -a -f database.sql && make install
