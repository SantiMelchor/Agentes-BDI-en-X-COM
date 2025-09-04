#!/bin/bash

for i in {0..19}; do
    docker exec prosody prosodyctl register soporteAzul_$i localhost 1234
    docker exec prosody prosodyctl register francotiradorAzul_$i localhost 1234
    docker exec prosody prosodyctl register pesadaAzul_$i localhost 1234
    docker exec prosody prosodyctl register asaltoAzul_$i localhost 1234
    docker exec prosody prosodyctl register soporteRojo_$i localhost 1234
    docker exec prosody prosodyctl register francotiradorRojo_$i localhost 1234
    docker exec prosody prosodyctl register pesadaRojo_$i localhost 1234
    docker exec prosody prosodyctl register asaltoRojo_$i localhost 1234
    docker exec prosody prosodyctl register tablero_$i localhost 1234
done
