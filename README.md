# Experiments with strategies for indexing HEALPix raster data

## Set up

```
$ docker-compose build
```

## Run benchmarks

```
$ docker-compose down && docker-compose run --rm example
Stopping healpix-intersection-example_postgres_1 ... done
Removing healpix-intersection-example_postgres_1 ... done
Removing network healpix-intersection-example_default
Creating network "healpix-intersection-example_default" with the default driver
Creating healpix-intersection-example_postgres_1 ... done
    2020-02-05 20:41:24,651 INFO generated new fontManager
*** create tables - 0.1 s
    2020-02-05 20:41:24,911 INFO downloading and reading ZTF field list
    2020-02-05 20:41:25,263 INFO building footprint polygons
    2020-02-05 20:41:25,273 INFO building MOCs
    2020-02-05 20:41:44,517 INFO creating ORM records
    2020-02-05 20:42:01,059 INFO saving
    2020-02-05 20:43:10,048 INFO done
*** load ZTF fields - 105.3 s
    2020-02-05 20:43:10,052 INFO querying GraceDB: "category: MDC 1264884208 .. 1264970608"
    2020-02-05 20:43:11,593 INFO downloading sky map for MS200205t
    2020-02-05 20:43:12,712 INFO creating ORM records
    2020-02-05 20:43:14,055 INFO saving
    2020-02-05 20:43:14,318 INFO committing
    2020-02-05 20:43:16,323 INFO done
*** load example LIGO sky map - 6.3 s
*** top 10 fields by probability - 3.1 s
```

