import sqlite3
import re
import sys

print('selected database :'+str(sys.argv[1]))
#utilisy functions:
#connect to the database and create a cursor


def connection(dbname):
    #connect to the database
    return_value = "conn = sqlite3.connect('"+dbname+"')\n"

    #create a cursor
    return_value += "\t\tcur=conn.cursor()\n"

    return return_value
#getting all the data from a table and jsonify it (get method)
def selectall(dbname,table):
    #connection
    return_value = connection(dbname)

    #get data + description
    return_value += "\t\trows = cur.execute('SELECT * FROM " +table+"').fetchall()\n"
    return_value += "\t\tjsdata=[dict(zip([desc[0] for desc in cur.description],row)) for row in rows]\n"

    #closing the database
    return_value+="\t\tconn.close()\n"

    #the return of the get method
    return_value+="\t\treturn jsonify({'data':jsdata})\n"
    
    return return_value

def post_new_data(dbname,table,columns):
    #connection
    return_value = connection(dbname)

    #adding the columns to the parser
    for col in columns[1:]:
        return_value += "\t\tparser.add_argument('{}')\n".format(col)
    return_value += "\t\targs = parser.parse_args()\n"
    return_value += "\t\tinserting =\"insert into "+table + \
        " values(NULL,"+",".join(['?' for _ in columns[1:]])+")\"\n"

    #executing the query:
    return_value += "\t\tcur.execute(inserting,(args['"+"'],args['".join(columns[1:])+"']))\n"
    #closing the database

    return_value += "\t\tconn.commit()\n"
    return_value += "\t\tconn.close()\n"
    return_value += "\t\treturn 'your {} has been added',201".format(table)
    return return_value
#index route response :
def url_mapping():
    return_value="\n#index:\n"
    return_value+="@app.route('/')\n"
    return_value+="def index():\n"
    return_value+="\treturn str(app.url_map)\n\n"

    return return_value

#--------------------------------
pattern = re.compile(r"[/\\]")
database_path = sys.argv[1]
database_name = re.split(pattern,database_path)[:].pop()
models_filename=database_name.split('.')[0]+"_models.py"

requirements = ['sqlite3','flask','flask_restful']
#--------------------------------

#Connect to sqlite database and get tables names
try:
    conn = sqlite3.connect(database_name)
    c=conn.cursor()
    #Query to get database datbes names
    meta_query="""
    SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
                """
    c.execute(meta_query)
    table_names = c.fetchall()
    #making a list of the names
    table_names = [x[0] for x in table_names]

    tables_columns = []
    for table_name in table_names:
        columns_query = """
        SELECT * FROM {}
            WHERE 1=0;
                    """.format(table_name)
        c.execute(columns_query)
        #columns = c.fetchall()
        #making a list of the names
        tables_columns.append([x[0] for x in c.description])
    conn.close()
    table_and_its_columns=list(zip(table_names,tables_columns))

except Exception as e:
    print(e)


#creating a new file and writing models
with open(models_filename,'w+') as model_file:
    #imports
    script="from flask import Flask,jsonify\nfrom flask_restful import Resource, Api, reqparse,abort\nimport sqlite3\n\n"
    
    #Configs
    script+="app = Flask(__name__)\napi = Api(app)\n"

    #parser
    script += "parser = reqparse.RequestParser()\n\n"

    #adding database
    script+="try:\n\tconn = sqlite3.connect('{}')\nexcept:\n\tprint('error connecting to the database')\n\n".format(database_name)
    
    #showing off
    script+="#script generated by instantAPI author:Mehdi\n\n"
    
    #writing the models
    #get and post
    for table_name,table_columns in table_and_its_columns:
        script += "class {0}List(Resource):\n\tdef get(self):\n\t\t{1}\n\tdef post(self):\n\t\t{2}\napi.add_resource({0}List,'/{0}/')\n\n".format(
            table_name, selectall(database_name, table_name), post_new_data(database_name, table_name,table_columns))
        a = post_new_data(database_name, table_name,table_columns)
    script+=url_mapping()
    #adding the flask run in debug mode
    script+='if __name__ == "__main__":\n\tapp.run(debug=True)'

    model_file.write(script)


    #requirements file:
    with open(database_name+'_requirements.txt','w+') as req:
        for r in requirements:
            req.write(r+"\n")


    #return_value+="args = parser.parse_args()\n"
    #if len(columns[1:]) == 1:
    #    return_value += ("\t\tinserting =\"insert into "+table +
    #                     "("+str(columns[1])+")values")
    #else:
    #    return_value += ("\t\tinserting =\"insert into "+table+"" +
    #                     str(tuple(columns[1:]))+"values")
