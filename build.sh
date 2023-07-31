#!/usr/bin/env bash

make install && psql -a -f database.sql
