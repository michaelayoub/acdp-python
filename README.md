# acdp-python

This is a grab-bag of code around ACDP. The main item of interest is `pull_pois_from_mysql.py`
and the script `pull_pois.sh` which will run it (after `config.env.example` has been copied to
`config.env` and the appropriate values filled in) and pull data from the `points_of_interest`
table and write them to a Protobuf file `POIsDB.binpb` used by the `ace_nearest_poi` UDF (found
in [acdp-ksql-udfs](https://github.com/michaelayoub/acdp-ksql-udfs)).
