from pyspark.sql import SparkSession
from pyspark.sql.types import *
import os

os.environ["JAVA_HOME"] = "C:/Program Files/Java/jdk-21" 
os.environ["HADOOP_HOME"] = "C:/hadoop"
spark = SparkSession.builder \
        .appName('primeros_pasos') \
        .master("local[*]") \
        .config("spark.driver.host", "localhost") \
        .getOrCreate()

sc = spark.sparkContext

def funcion_secundaria():
    df_doctor = spark.read.format ("csv").option("header", "true").load("Practica_Provisionales.csv")
    df_doctor.show(1)

def main():
    funcion_secundaria()
    
if __name__ == "__main__":
    main()
