# Experiments with strategies for indexing HEALPix raster data

## Set up

```
$ docker-compose build
```

## Run benchmarks

```
$ docker-compose down && docker-compose run --rm example
$ docker-compose down && docker-compose run --rm example
Stopping healpix-intersection-example_postgres_1 ... done
Removing healpix-intersection-example_postgres_1 ... done
Removing network healpix-intersection-example_default
Creating network "healpix-intersection-example_default" with the default driver
Creating healpix-intersection-example_postgres_1 ... done
    2020-02-07 20:19:24,659 INFO generated new fontManager
    2020-02-07 20:19:24,855 INFO Loading KWallet
    2020-02-07 20:19:24,856 INFO Loading SecretService
    2020-02-07 20:19:24,869 INFO Loading Windows
    2020-02-07 20:19:24,870 INFO Loading chainer
    2020-02-07 20:19:24,870 INFO Loading macOS
*** create tables - 0.1 s
    2020-02-07 20:19:25,052 INFO downloading and reading ZTF field list
    2020-02-07 20:19:25,456 INFO building footprint polygons
    2020-02-07 20:19:25,467 INFO building MOCs
    2020-02-07 20:19:43,315 INFO creating ORM records
    2020-02-07 20:19:59,274 INFO saving
    2020-02-07 20:21:08,468 INFO done
*** load ZTF fields - 103.6 s
    2020-02-07 20:21:08,476 INFO querying GraceDB: "category: MDC 1265055686 .. 1265142086"
    2020-02-07 20:21:10,513 INFO downloading sky map for MS200207t
    2020-02-07 20:21:11,884 INFO creating ORM records
    2020-02-07 20:21:13,210 INFO saving
    2020-02-07 20:21:13,460 INFO committing
    2020-02-07 20:21:15,501 INFO done
*** load example LIGO sky map - 7.0 s
    2020-02-07 20:21:15,502 INFO loading 2MRS from VizieR
    2020-02-07 20:21:19,182 INFO converting to HEALPix
    2020-02-07 20:21:19,203 INFO creating ORM records
    2020-02-07 20:21:22,165 INFO saving
    2020-02-07 20:21:24,237 INFO done
*** loading 2MRS catalog - 8.7 s
*** top 10 fields by probability - 2.9 s
*** top 10 galaxies by probability density - 0.4 s
*** top 10 fields by galaxy count - 1.1 s
```
