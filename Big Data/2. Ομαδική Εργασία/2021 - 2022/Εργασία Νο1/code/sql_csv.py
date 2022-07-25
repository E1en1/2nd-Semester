import findspark
findspark.init()
from pyspark.sql import SparkSession
import time

spark = SparkSession.builder.appName("sql_query_X").config("spark.executor.memory", "2g").config("spark.executor.cores", "2").getOrCreate()
sc = spark.sparkContext

# adjust the HDFS path
path = "/"

filesfolder = "files/"

# Loading the .csv files and fixing headers
csv_names = ["artists","charts","regions","chart_artist_mapping"]
dfs = []

for name in csv_names:
    dfs.append(spark.read.option("header","false").option("inferSchema","true").csv(path+filesfolder+name+".csv"))

dfs[0] = dfs[0].withColumnRenamed("_c0","ART_ID").withColumnRenamed("_c1","ART_NAME")
dfs[0].createOrReplaceTempView("ARTS")

dfs[1] = dfs[1].withColumnRenamed("_c0","SONG_ID").withColumnRenamed("_c1","SONG_NAME").withColumnRenamed("_c2","POS").\
                withColumnRenamed("_c3","DATE").withColumnRenamed("_c4","REG_ID").withColumnRenamed("_c5","CHART").\
                withColumnRenamed("_c6","ACTION").withColumnRenamed("_c7","STREAMS")
dfs[1].createOrReplaceTempView("CHARTS")

dfs[2] = dfs[2].withColumnRenamed("_c0","REG_ID").withColumnRenamed("_c1","REG_NAME")
dfs[2].createOrReplaceTempView("REGIONS")

dfs[3] = dfs[3].withColumnRenamed("_c0","SONG_ID").withColumnRenamed("_c1","ART_ID")
dfs[3].createOrReplaceTempView("CHARTARTS")

# a list to track the execution times
# WARNING! Track the execution time only the first time of collection
dts_a = []

# Query No. 1

Query_1 = "SELECT SUM(STREAMS) AS result "+\
          "FROM CHARTS "+\
          "WHERE (SONG_NAME = 'Shape of You' AND CHART = 'top200')"

tick = time.time()
res_1 = spark.sql(Query_1).collect()[0][0]
tack = time.time()

dts_a.append(tack-tick)

# Start with a blank .txt every time the script is run
with open("../outputs/CSV_Queries.txt", 'w', encoding="utf-8") as f :
	f.write('')
with open("../outputs/CSV_times.csv", 'w', encoding="utf-8") as ft :
	ft.write('')


with open("../outputs/CSV_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 1 - SQL Version - CSV File\n"+55*"-"+"\n")
    output_f.write(str(res_1)+"\n\n")

with open("../outputs/CSV_times.csv",'a') as times_f:
    times_f.write("Query 1, {}  \n".format(dts_a[0]))

# Query No. 2

Query_2_a = "SELECT CHART, SONG_NAME, COUNT(*)/69 AS OCCS "+\
            "FROM CHARTS "+\
            "WHERE (POS = 1) "+\
            "GROUP BY CHART, SONG_NAME "+\
            "ORDER BY OCCS DESC"

Query_2_b = "SELECT S.* FROM SUBQT S "+\
            "INNER JOIN (SELECT CHART, MAX(OCCS) AS MAXOCC FROM SUBQT GROUP BY CHART) MXS "+\
            "ON S.OCCS = MXS.MAXOCC "

# Time only the query execution + collection
tick = time.time()
spark.sql(Query_2_a).createOrReplaceTempView("SUBQT")
res_2 = spark.sql(Query_2_b).collect()
tack = time.time()

dts_a.append(tack-tick)

with open("../outputs/CSV_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 2 - SQL Version - CSV File\n"+55*"-"+"\n")
    for row in res_2:
        itm = list(row.asDict().values())
        output_f.write("{}, {}, {} \n".format(itm[0], itm[1], itm[2]))
    output_f.write("\n\n")

with open("../outputs/CSV_times.csv",'a') as times_f:
    times_f.write("Query 2, {} \n".format(dts_a[1]))

# Query No. 3

Query_3 = "SELECT YEAR(DATE) AS Year, MONTH(DATE) AS Month, SUM(STREAMS)/MAX(DAY(DATE)) AS StreamsSum "+\
          "FROM CHARTS "+\
          "WHERE (POS = 1 AND CHART = 'top200') "+\
          "GROUP BY Year, Month " +\
          "ORDER BY Year, Month"

tick = time.time()
res_3 = spark.sql(Query_3).collect()
tack = time.time()

dts_a.append(tack-tick)

with open("../outputs/CSV_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 3 - SQL Version - CSV File\n"+55*"-"+"\n")
    for row in res_3:
        itm = list(row.asDict().values())
        output_f.write("{}, {}, {}, \n".format(itm[0], itm[1], itm[2]))
    output_f.write("\n\n")

with open("../outputs/CSV_times.csv",'a') as times_f:
    times_f.write("Query 3, {}  \n".format(dts_a[2]))

# Query No. 4

Query_4_a = "SELECT REG_ID, SONG_ID, SONG_NAME, COUNT(*) AS CT "+\
            "FROM CHARTS "+\
            "WHERE (CHART = 'viral50') "+\
            "GROUP BY REG_ID, SONG_ID, SONG_NAME "+\
            "ORDER BY CT DESC, REG_ID"

Query_4_b = "SELECT R.REG_NAME, CTT.SONG_ID, CTT.SONG_NAME, CTT.CT "+\
            "FROM CTTABLE CTT "+\
            "INNER JOIN (SELECT REG_ID, MAX(CT) AS MaxCT FROM CTTABLE GROUP BY REG_ID) GROUPEDCTT "+\
            "ON CTT.REG_ID = GROUPEDCTT.REG_ID AND CTT.CT = GROUPEDCTT.MaxCT "+\
            "INNER JOIN REGIONS R ON CTT.REG_ID = R.REG_ID "+\
            "ORDER BY R.REG_NAME, CTT.SONG_ID "

tick = time.time()
spark.sql(Query_4_a).createOrReplaceTempView("CTTABLE")
res_4 = spark.sql(Query_4_b).collect()
tack = time.time()

dts_a.append(tack-tick)

with open("../outputs/CSV_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 4 - SQL Version - CSV File\n"+55*"-"+"\n")
    for row in res_4:
        itm = list(row.asDict().values())
        output_f.write("{}, {}, {}, {} \n".format(itm[0], itm[1], itm[2], itm[3]))
    output_f.write("\n\n")

with open("../outputs/CSV_times.csv",'a') as times_f:
    times_f.write("Query 4, {}  \n".format(dts_a[3]))

# Query No. 5

Query_5_a = "SELECT YEAR(C.DATE) AS YR, A.ART_NAME, SUM(C.STREAMS)/69 AS SSTR "+\
            "FROM CHARTS C "+\
            "INNER JOIN CHARTARTS CAM "+\
            "ON CAM.SONG_ID = C.SONG_ID "+\
            "INNER JOIN ARTS A "+\
            "ON A.ART_ID = CAM.ART_ID "+\
            "WHERE (C.CHART = 'top200') "+\
            "GROUP BY YR, A.ART_NAME "

Query_5_b = "SELECT S.* FROM SST S "+\
            "INNER JOIN (SELECT YR, MAX(SSTR) AS MSSTR FROM SST GROUP BY YR) GROUPEDS "+\
            "ON S.SSTR = GROUPEDS.MSSTR "+\
            "ORDER BY S.YR"

tick = time.time()
spark.sql(Query_5_a).createOrReplaceTempView("SST")
res_5 = spark.sql(Query_5_b).collect()
tack = time.time()

dts_a.append(tack-tick)

with open("../outputs/CSV_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 5 - SQL Version - CSV File\n"+55*"-"+"\n")
    for row in res_5:
        itm = list(row.asDict().values())
        output_f.write("{}, {}, {} \n".format(itm[0], itm[1], itm[2]))
    output_f.write("\n\n")

with open("../outputs/CSV_times.csv",'a') as times_f:
    times_f.write("Query 5, {} \n ".format(dts_a[4]))


# Query No. 6 - FIRST INTERPRETATION (SEE REPORT)

"""from pyspark.sql import Window 
from pyspark.sql import functions as f

tick = time.time()
# Basic filters
regid = dfs[2].filter("REG_NAME=='Greece'").select(f.col("REG_ID")).collect()[0][0]
fdf = dfs[1].filter(f"REG_ID=={regid}").filter("POS=1").orderBy(dfs[1].DATE.asc())
# We only care for the SAME_POSITION value to count consecutive tops
fdf = fdf.withColumn("ACTION", f.when(fdf.ACTION == "SAME_POSITION",1).otherwise(0))
# Set time windows to be able to count consecutive rows of ACTION = SAME_POSITION
w1 = Window.partitionBy(fdf.SONG_NAME,fdf.CHART).orderBy(fdf.DATE)
w2 = Window.partitionBy(fdf.SONG_NAME,fdf.CHART,fdf.ACTION).orderBy(fdf.DATE)
res = fdf.withColumn('grp',f.row_number().over(w1)-f.row_number().over(w2))
w3 = Window.partitionBy(res.SONG_NAME,res.CHART,res.ACTION,res.grp).orderBy(res.DATE)
streak_res = res.withColumn('streak',f.when(res.ACTION == 0,0).otherwise(f.row_number().over(w3)))
# Add one to account for the zeroth entry and order chronologically
streak_res = streak_res.withColumn('streak', f.col('streak') + f.lit(1)).orderBy(streak_res.DATE)
# Get yearly results
fw = Window.partitionBy(f.col("CHART"),f.year("DATE"))
streak_res = streak_res.withColumn('maxStreak', f.max('streak').over(fw)).where(f.col('streak')==f.col('maxStreak')).drop('maxStreak').orderBy(streak_res.DATE)

# Gather the other information from joins
upddf = streak_res.join(dfs[3],streak_res.SONG_ID == dfs[3].SONG_ID,"inner")
upddf = upddf.join(dfs[0],upddf.ART_ID == dfs[0].ART_ID, "inner")
upddf = upddf.orderBy(f.col("CHART"),f.col("DATE")).select(f.col("CHART"),f.year(f.col("DATE")),f.col("ART_NAME"),f.col("streak"))

res_6 = upddf.collect()
tack = time.time()

dts_a.append(tack-tick)"""
    
# Query No. 6 - THIRD INTERPRETATION (SEE REPORT)

Query_6_a = "SELECT C.CHART, YEAR(C.DATE) AS Year, C.SONG_ID, COUNT(*) AS CT "+\
            "FROM CHARTS C "+\
            "INNER JOIN REGIONS R "+\
            "ON C.REG_ID = R.REG_ID "+\
            "WHERE (POS = 1 AND ACTION = 'SAME_POSITION' AND R.REG_NAME = 'Greece') "+\
            "GROUP BY CHART, Year, SONG_ID "

Query_6_b = "SELECT TV.CHART, TV.Year, A.ART_NAME, TV.CT "+\
            "FROM TMPV TV "+\
            "INNER JOIN (SELECT CHART, Year, MAX(CT) AS MaxCT FROM TMPV GROUP BY CHART, Year) GROUPEDTV "+\
            "ON TV.CHART = GROUPEDTV.CHART AND TV.Year = GROUPEDTV.Year AND TV.CT = GROUPEDTV.MaxCT "+\
            "INNER JOIN CHARTARTS CAM ON CAM.SONG_ID = TV.SONG_ID "+\
            "INNER JOIN ARTS A ON A.ART_ID = CAM.ART_ID "+\
            "ORDER BY TV.CHART, TV.Year "

tick = time.time()
spark.sql(Query_6_a).createOrReplaceTempView("TMPV")
res_6 = spark.sql(Query_6_b).collect()
tack = time.time()

dts_a.append(tack-tick)

with open(path+"outputs/CSV_Queries.txt",'a', encoding="utf-8") as output_f:
    output_f.write(55*"-"+"\nQuery 6 - SQL Version - CSV File\n"+55*"-"+"\n")
    for row in res_6:
        itm = list(row.asDict().values())
        output_f.write("{} {} {} {} \n".format(itm[0], itm[1], itm[2], itm[3]))

with open(path+"outputs/CSV_times.csv",'a') as times_f:
    times_f.write("Query 6, \n".format(dts_a[5]))

