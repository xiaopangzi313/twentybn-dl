#!/bin/sh

BASE_URL="https://s3-eu-west-1.amazonaws.com/20bn-public-datasets"
BIGTGZ="20bn-something-something-v1.tgz"
TAR_BASE="20bn-something-something-v1"
BIGTGZ_SIZE="30677157329"
TGZ_EXPECTED="134636"

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
  wget -nv -c "$BASE_URL/something-something/v1/$c"
done

if [ $(stat --printf="%s" $BIGTGZ) -eq $BIGTGZ_SIZE ] ; then
    echo "$BIGTGZ is (probably) up to date"
else
    echo "will not cat chunks..."
    cat $CHUNKS > $BIGTGZ
    echo "done."
fi

if [ $( find $TAR_BASE -name '*.tar' | wc -l ) -eq $TGZ_EXPECTED ] ; then
    echo "tar files are (probably) up to date"
else
    tar xvzf $BIGTGZ
fi

for f in $( find $TAR_BASE -name '*.tar')
do
  tar -C 20bn-something-something-v1/ -xvf $f
done


