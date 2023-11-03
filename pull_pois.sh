#!/bin/sh

env $(cat config.env | xargs) python pull_pois_from_mysql.py