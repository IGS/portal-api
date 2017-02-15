import urllib2, re, json
from multiprocessing import Process, Queue, Pool

# The match var is the base query to prepend all queries. The idea is to traverse
# the graph entirely and use filters to return a subset of the total traversal. 
match = ("MATCH (Project:Case{node_type:'project'})<-[:PART_OF]-(Study:Case{node_type:'study'})"
    "<-[:PARTICIPATES_IN]-(Subject:Case{node_type:'subject'})"
    "<-[:BY]-(Visit:Case{node_type:'visit'})"
    "<-[:COLLECTED_DURING]-(Sample:Case{node_type:'sample'})"
    "<-[:PREPARED_FROM]-(pf)"
    "<-[:SEQUENCED_FROM|DERIVED_FROM|COMPUTED_FROM*..4]-(File) WHERE "
    )

# If the following return ends in "counts", then it is for a pie chart. The first two are for
# cases/files tabs and the last is for the total size. 
#
# All of these returns are pre-pended with "WITH DISTINCT File.*". This is because there is 
# some redundancy in the HMP data in that some nodes are iterated over multiple times. In order 
# to get around this, need to just return each file that is seen only once and bundle any of the
# other nodes alongside this single file. Meaning, "WITH DISTINCT File,Project" and only returning
# aspects of 'Project' like Project.name or something is only counted once along a given path to a 
# particular file. Note that each one has a fairly unique "WITH DISTINCT" clause, this is to help
# optimize the query and ensure the distinct check is as simple as the return allows it to be.

# The detailed queries require specifics about both sample and file counts to be 
# returned so they require some extra handling. 
base_detailed_return = ("WITH (COUNT(DISTINCT(Sample))) as ccounts, "
    "COUNT(DISTINCT(File)) AS dcounts, %s.%s AS prop, "
    "collect(DISTINCT File) AS f UNWIND f AS fs "
    "RETURN prop,ccounts,dcounts,SUM(toInt(fs.size)) as tot"
    )

returns = {
    'cases': "WITH DISTINCT Project,Sample,Study RETURN Project.name, Project.subtype, Sample.fma_body_site, Sample.id, Study.subtype",
    'files': "WITH DISTINCT File,Project,Sample RETURN Project, File, Sample.id",
    'name': "WITH DISTINCT File,Project RETURN Project.name as prop, count(Project.name) as counts",
    'name_detailed': base_detailed_return % ('Project','name'),
    'sname': "WITH DISTINCT File,Study RETURN Study.name as prop, count(Study.name) as counts",
    'sname_detailed': base_detailed_return % ('Study','name'),
    'fma_body_site': "WITH DISTINCT File,Sample RETURN Sample.fma_body_site as prop, count(Sample.fma_body_site) as counts",
    'fma_body_site_detailed': base_detailed_return % ('Sample','fma_body_site'), 
    'study': "WITH DISTINCT File,Study RETURN Study.name as prop, count(Study.name) as counts",
    'gender': "WITH DISTINCT File,Subject RETURN Subject.gender as prop, count(Subject.gender) as counts",
    'gender_detailed': base_detailed_return % ('Subject','gender'),
    'race': "WITH DISTINCT File,Subject RETURN Subject.race as prop, count(Subject.race) as counts",
    'format': "WITH DISTINCT File RETURN File.format as prop, count(File.format) as counts",
    'format_detailed': base_detailed_return % ('File','format'),
    'subtype_detailed': base_detailed_return % ('File','subtype'),
    'size': "WITH DISTINCT File RETURN (SUM(toInt(File.size))) as tot",
    'f_pagination': "WITH DISTINCT File RETURN (count(File)) AS tot",
    'c_pagination': "WITH DISTINCT Sample RETURN (count(Sample.id)) AS tot"
}

# Function to extract known GDC syntax and convert to OSDF. This is commonly needed for performing
# cypher queries while still being able to develop the front-end with the cases syntax.
def convert_gdc_to_osdf(inp_str):
    # Errors in Graphene mapping prevent the syntax I want, so ProjectName is converted to 
    # Cypher ready Project.name here (as are the other possible query parameters).
    inp_str = inp_str.replace("cases.ProjectName","Project.name")
    inp_str = inp_str.replace("cases.SampleFmabodysite","Sample.fma_body_site")
    inp_str = inp_str.replace("cases.SubjectGender","Subject.gender")
    inp_str = inp_str.replace("project.primary_site","Sample.fma_body_site")
    inp_str = inp_str.replace("subject.gender","Subject.gender")
    inp_str = inp_str.replace("study.name","Study.name")
    inp_str = inp_str.replace("file.format","File.format")
    inp_str = inp_str.replace("file.category","File.subtype") # note the conversion
    inp_str = inp_str.replace("files.file_id","File.id")
    inp_str = inp_str.replace("cases.","") # these replaces have to be catch alls to replace all instances throughout
    inp_str = inp_str.replace("file.","")
    inp_str = inp_str.replace("sample.","")
    inp_str = inp_str.replace("Project_","Project.")
    inp_str = inp_str.replace("Sample_","Sample.")
    inp_str = inp_str.replace("SampleAttr_","SampleAttr.")
    inp_str = inp_str.replace("Study_","Study.")
    inp_str = inp_str.replace("Subject_","Subject.")
    inp_str = inp_str.replace("SubjectAttr_","SubjectAttr.")
    inp_str = inp_str.replace("Visit_","Visit.")
    inp_str = inp_str.replace("VisitAttr_","VisitAttr.")
    inp_str = inp_str.replace("File_","File.")

    # Handle facet searches from panel on left side
    inp_str = inp_str.replace("data_type","File.node_type")
    inp_str = inp_str.replace("data_format","File.format")

    # Next two lines guarantee URL encoding (seeing errors with urllib)
    inp_str = inp_str.replace('"','|')
    inp_str = inp_str.replace('\\','')
    inp_str = inp_str.replace(" ","%20")

    # While the DB is to be set at read-only, in the case this toggle is 
    # forgotten do some checks to make sure nothing fishy is happening.
    potentially_malicious = set([";"," delete "," create "," detach "," set ",
                                " return "," match "," merge "," where "," with ",
                                " import "," remove "," union "])
    check_str = inp_str.lower()
    for word in check_str:
        if word in potentially_malicious:
            break

    return inp_str

# This is a recursive function originally used to traverse and find the depth 
# of nested JSON. Now used to traverse the op/filters query from GDC and 
# ultimately aims to provide input to build the WHERE clause of a Cypher query. 
# Accepts input of json.loads parsed GDC portal query input and an empty array. 
# Note that this is currently only called when facet search is being performed.
def get_depth(x, arr):
    if type(x) is dict and x:
        if 'op' in x:
            arr.append(x['op'])
        if 'field' in x:
            left = x['field']
            right = x['value']
            if type(x['value']) is list:
                l = x['value']
                l = ["'{0}'".format(element) for element in l] # need to add quotes around each element to make Cypher happy
                right = ",".join(l)
            else:
                right = "'{0}'".format(right) # again, quotes for Cypher
            arr.append(left)
            arr.append(right)
        return max(get_depth(x[a], arr) for a in x)
    if type(x) is list and x: 
        return max(get_depth(a, arr) for a in x)
    return arr # give the array back after traversal is complete

# Fxn to build Cypher based on facet search, accepts output from get_depth
def build_facet_where(inp): 
    facets = [] # going to build an array of all the facets params present
    lstr, rstr = ("" for i in range(2))
    for x in reversed(range(0,len(inp))):
        if "'" in inp[x]: # found the values to search for
            rstr = "[%s]" % (inp[x]) # add brackets for Cypher
        elif "." in inp[x]: # found the fields to search on
            lstr = inp[x]
        elif "in" == inp[x]: # found the comparison op, build the full string
            facets.append("%s in %s" % (lstr, rstr))
    return " AND ".join(facets) # send back Cypher-ready WHERE clause

# Final function needed to build the entirety of the Cypher query taken from facet search. Accepts the following:
# match = base MATCH query for Cypher
# whereFilters = filters string passed from GDC portal
# order = parameters to order results by (needed for pagination)
# start = index of sort to start at
# size = number of results to return
# rtype = return type, want to be able to hit this for both cases, files, and aggregation counts.
def build_cypher(match,whereFilters,order,start,size,rtype):
    arr = []
    q = json.loads(whereFilters) # parse filters input into JSON (yields hashes of arrays)
    w1 = get_depth(q, arr) # first step of building where clause is the array of individual comparison elements
    where = build_facet_where(w1)
    where = where.replace("cases.","") # trim the GDC syntax, hack until we refactor cases/files syntax
    where = where.replace("files.","")
    order = order.replace("cases.","")
    order = order.replace("files.","")
    retval1 = returns[rtype] # actual RETURN portion of statement
    if rtype in ["cases","files"]: # pagination handling needed for these returns
        order = order.split(":")
        if start != 0:
            start = start - 1
        retval2 = "ORDER BY %s %s SKIP %s LIMIT %s" % (order[0],order[1].upper(),start,size) 
        return "%s %s %s %s" % (match,where,retval1,retval2)
    else:
        return "%s %s %s" % (match,where,retval1)

# First iteration, handling all regex individually
regexForNotEqual = re.compile(r"<>\s([0-9]*[a-zA-Z_]+[a-zA-Z0-9_]*)\b") # only want to add quotes to anything that's not solely numbers
regexForEqual = re.compile(r"=\s([0-9]*[a-zA-Z_]+[a-zA-Z0-9_]*)\b") 
regexForIn = re.compile(r"(\[[a-zA-Z\'\"\s\,\(\)]+\])") # catch anything that should be in a list

# This advanced Cypher builder expects the string generated by any of the advanced queries. 
# Parameters are described above before build_cypher()
def build_adv_cypher(match,whereFilters,order,start,size,rtype):
    where = whereFilters[10:len(whereFilters)-2] 
    where = where.replace("!=","<>")

    # Add quotes that FE missed
    if '=' in where:
        where = regexForEqual.sub(r'= "\1"',where)
    if '<>' in where:
        where = regexForNotEqual.sub(r'<> "\1"',where)
    if ' in ' in where or ' IN ' in where: # lists present, parse through and add quotes to all values without them
        lists = re.findall(regexForIn,where)
        listDict = {}
        for extractedList in lists:
            original = extractedList
            extractedList = extractedList.replace('[','')
            extractedList = extractedList.replace(']','')
            indivItems = extractedList.split(',')
            newList = []
            for item in indivItems:
                if '"' in item:
                    parts = re.split(r"""("[^"]*"|'[^']*')""", item) # remove spaces outside quotes
                    parts[::2] = map(lambda s: "".join(s.split()), parts[::2])
                    newList.append("".join(parts))
                else:
                    item = item.replace(" ","")
                    newList.append('"%s"' % (item))
            extractedList = ",".join(newList)
            new = "[%s]" % (extractedList)
            listDict[original] = new

        for k,v in listDict.iteritems():
            where = where.replace(k,v)

    order = order.replace("cases.","")
    order = order.replace("files.","")
    retval1 = returns[rtype] # actual RETURN portion of statement
    if rtype in ["cases","files"]: # pagination handling needed for these returns
        order = order.split(":")
        if start != 0:
            start = start-1
        retval2 = "ORDER BY %s %s SKIP %s LIMIT %s" % (order[0],order[1].upper(),start,size)
        if size == 0: # accounting for inconsistency where front-end asks for a 0 size return
            retval2 = "ORDER BY %s %s" % (order[0],order[1].upper())
        return "%s %s %s %s" % (match,where,retval1,retval2)
    else:
        return "%s %s %s" % (match,where,retval1)
