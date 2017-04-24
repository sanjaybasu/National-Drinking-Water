#!/bin/bash

pg_dump drinking_water --clean --no-owner -f drinking_water.sql
