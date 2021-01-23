set -e
cd data

wget https://s3.amazonaws.com/tripdata/201901-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201902-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201903-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201904-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201905-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201906-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201907-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201908-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201909-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201910-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201911-citibike-tripdata.csv.zip
wget https://s3.amazonaws.com/tripdata/201912-citibike-tripdata.csv.zip

unzip 201901-citibike-tripdata.csv.zip
unzip 201902-citibike-tripdata.csv.zip # contains a stray __MAXOSX folder
unzip 201903-citibike-tripdata.csv.zip
unzip 201904-citibike-tripdata.csv.zip
unzip 201905-citibike-tripdata.csv.zip
unzip 201906-citibike-tripdata.csv.zip
unzip 201907-citibike-tripdata.csv.zip
unzip 201908-citibike-tripdata.csv.zip
unzip 201909-citibike-tripdata.csv.zip
unzip 201910-citibike-tripdata.csv.zip
unzip 201911-citibike-tripdata.csv.zip
unzip 201912-citibike-tripdata.csv.zip

echo 'Cleaning up unused zip files'
rm *.zip
if [ -d __MACOSX ]; then rm -Rf __MACOSX; fi
echo 'Finished! Data is ready for ingestion'
