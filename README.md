# Experiments with strategies for indexing HEALPix raster data

## Set up

```
$ docker-compose build
```

## Run benchmarks

```
$ docker-compose down && docker-compose run --rm example
Removing network healpix-intersection-example_default
Creating network "healpix-intersection-example_default" with the default driver
Creating healpix-intersection-example_postgres_1 ... done
    2020-02-07 19:56:46,885 INFO generated new fontManager
    2020-02-07 19:56:47,188 INFO Loading KWallet
    2020-02-07 19:56:47,191 INFO Loading SecretService
    2020-02-07 19:56:47,216 INFO Loading Windows
    2020-02-07 19:56:47,217 INFO Loading chainer
    2020-02-07 19:56:47,219 INFO Loading macOS
*** create tables - 0.1 s
    2020-02-07 19:56:47,508 INFO downloading and reading ZTF field list
    2020-02-07 19:56:48,153 INFO building footprint polygons
    2020-02-07 19:56:48,159 INFO building MOCs
    2020-02-07 19:57:07,228 INFO creating ORM records
    2020-02-07 19:57:25,934 INFO saving
    2020-02-07 19:58:38,011 INFO done
*** load ZTF fields - 110.6 s
    2020-02-07 19:58:38,014 INFO querying GraceDB: "category: MDC 1265054336 .. 1265140736"
    2020-02-07 19:58:39,884 INFO downloading sky map for MS200207t
    2020-02-07 19:58:41,852 INFO creating ORM records
    2020-02-07 19:58:43,241 INFO saving
    2020-02-07 19:58:43,821 INFO committing
    2020-02-07 19:58:45,847 INFO done
*** load example LIGO sky map - 7.9 s
    2020-02-07 19:58:45,849 INFO loading 2MRS from VizieR
    2020-02-07 19:58:49,447 INFO converting to HEALPix
    2020-02-07 19:58:49,458 INFO creating ORM records
    2020-02-07 19:58:51,778 INFO saving
    2020-02-07 19:58:53,820 INFO done
*** loading 2MRS catalog - 8.0 s
*** top 10 fields by probability - 3.1 s
*** top 10 galaxies by probability density - 0.4 s
```
