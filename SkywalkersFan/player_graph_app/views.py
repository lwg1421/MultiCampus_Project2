from http.client import HTTPResponse
import sqlite3 as sql
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def player(request) :
    return HttpResponse('player page')

def dbtodf(table_name):
    temp='select * from '+str(table_name)
    con=sql.connect('./SkywalkersFan/db.sqlite3')
    cur=con.cursor()
    query=cur.execute(temp)
    cols=[column[0] for column in query.description]
    result=pd.DataFrame.from_records(data=query.fetchall(),columns=cols)
    con.close()
    return result

# 그래프 그리는 함수들 만들기