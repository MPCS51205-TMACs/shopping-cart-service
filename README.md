# closed-auction-metrics

text / call Austin Clark for details 703-785-1134.

## Overview

## Developer notes

* put together hastily. chose python/mongo for the agility.

## Architecture

This context uses a layered architecture with code written python. mongodb is used for storage.

## persistence

## deployment


## to run tests 

There are little-to-no tests, but to run tests, use pytest with verbose and print-to-std-out flags.

E.g., cd to `domain/` and run
```
$ pytest tests/ -vs
```

Due to imports some tests might have to be run like so

```
$ python3 -m pytest domain/tests/test_auction.py  -vs
```

## starting the application

If firing up just this microservice, perform a docker-compose call using `docker-compose.yml`
```
$ docker-compose up -d
```

turn down with
```
$ docker-compose down
```