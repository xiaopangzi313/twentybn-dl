#!/bin/sh

BASE_URL="https://s3-eu-west-1.amazonaws.com/20bn-public-datasets"

CHUNKS="20bn-something-something-v1-aa
20bn-something-something-v1-ab
20bn-something-something-v1-ac
20bn-something-something-v1-ad
20bn-something-something-v1-ae
20bn-something-something-v1-af
20bn-something-something-v1-ag
20bn-something-something-v1-ah
20bn-something-something-v1-ai
20bn-something-something-v1-aj
20bn-something-something-v1-ak
20bn-something-something-v1-al
20bn-something-something-v1-am
20bn-something-something-v1-an
20bn-something-something-v1-ao
20bn-something-something-v1-ap
20bn-something-something-v1-aq
20bn-something-something-v1-ar
20bn-something-something-v1-as
20bn-something-something-v1-at
20bn-something-something-v1-au
20bn-something-something-v1-av
20bn-something-something-v1-aw
20bn-something-something-v1-ax
20bn-something-something-v1-ay
20bn-something-something-v1-az
20bn-something-something-v1-bb
20bn-something-something-v1-bc
20bn-something-something-v1-bd
20bn-something-something-v1-be"

for c in $CHUNKS
do
  wget -nv -c "$BASE_URL/something-something/v0/$c"
done
cat $CHUNKS | tar xvzf
