

hadoop fs -rmr outputdir 
hadoop fs -rmr outputdir2
rm results.txt

INPUT=testL/testLong.txt
JAR=/usr/lib/hadoop/contrib/streaming/hadoop-streaming-0.20.2-cdh3u2.jar
hadoop jar $JAR -input $INPUT -output outputdir -mapper fpMap.py -reducer fpReduce.py -file fpReduce.py -file fpMap.py  


hadoop jar $JAR -input outputdir/p* -output outputdir2 -mapper ruleMap.py -reducer ruleReduce.py -file ruleReduce.py -file ruleMap.py  

hadoop fs -cat outputdir2/part* > results.txt
