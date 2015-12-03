#Author: Gouri Ginde
#This program computes the selfcitations for 3 sub categories under Engg and Computer Science of GS
# Mainly AI, Evolutionary computation and Computing Systems
from BeautifulSoup import BeautifulSoup
from time import sleep
from random import choice
from csv import DictWriter
import urllib2
import sys
import json
import readFile
#import re
JInfo = [] 
year= ['2012', '2013', '2014', '2015']
h5_index = 0
count = 1
# create wait range between 20 and 40 seconds
r = range(20,60)

stopat1000 = 0
stopFortheDay = 0  #stop scraping for that day as the limit is just this! 2500
orig_stdout = sys.stdout
f = file('../dump/selfcites.txt', 'a')
#sys.stdout = f

def writeToFile(somestr):
    json.dump(somestr, f)
    
def checkForDwnldThreshold():
    #controlling the blocking of the program
    global stopat1000
    if stopat1000 > 900:
        sleep(3600)
        stopFortheDay = stopFortheDay + stopat1000
        stopat1000 = 0
    if stopFortheDay > 2400:
        sleep(86400)
        stopFortheDay = 0
     
    
def writeToSpreadsheet(dictItem):
    with open('../dump/spreadsheet.csv','a') as outfile:
        writer = DictWriter(outfile, ('Id, JName, Authors_name, YearOfPub, CitedByLink, CitesPerPaper, SelCitesPerPaper'))
        writer.writeheader()
        writer.writerows(dictItem)

def urlopener(url):
    opener = urllib2.build_opener()
    ####################################################################################################
    # different user agents to use to keep from being banned.
    user_agents = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'               
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1',
    ]
    version = choice(user_agents)
    #opener.addheaders = [('User-Agent', 'OpenAnything/1.0 +http://diveintopython.org/')]
    #Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0
    #opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0')]
    opener.addheaders = [('User-agent', version)]
    
    try:
        html_page = (opener.open(url)).read()
    except urllib2.HTTPError, err:
        print "Error code is: " , err.code
        print "Reason is: ", err.reason
        return False
    
        
    return html_page
# function to get the link to all papers of that Journal 
def getLinktoAllPapers( jName):
    url = "https://scholar.google.com/citations?hl=en&view_op=search_venues&vq="+jName
    html_page = urlopener(url)
    #html_page = urllib2.urlopen(url)
    if html_page!= False : 
        soup = BeautifulSoup(html_page)
        table = soup.find('table', {'id': 'gs_cit_list_table'})
        td_list = table.findAll("td")
        #print td_list 
        h5_indexSTR = td_list[2].text
        h5_medianSTR = td_list[3].text
        global h5_index 
        h5_index = int(h5_indexSTR)
        #print h5_index , h5_median
        venue = (td_list[2].find("a")).get('href')
        #print venue
        youRL = "https://scholar.google.com/"+ venue
        dict1 = {'JName': jName, 'h5_index' : h5_indexSTR, 'h5_median': h5_medianSTR, 'venue' : youRL };
        JInfo.append(dict1)
        writeToFile ("link to main is: "+youRL+"\n") 
        return youRL

#for every publication/paper in the journal compute the self-citation and add to the JInfo List
def getPubInfo(pubsLink, jName, pages):
    #pages = 20
    #list1 = [2]
    #dict1 = {'Id': '1', 'JName': "3D Research ", 'Authors_name': 'First', 'YearOfPub':2014, 'CitedByLink': 'test', 'CitesPerPaper':1000, 'SelCitesPerPaper':200 };
    #dict1['Author_name'] = "Gouri"; # update existing entry
    #list1[0] = dict1
    #dict2 = {'Id': '1', 'JName': "3D Research ", 'Authors_name': 'First', 'YearOfPub':2014 };
    #list1.append(dict2)
    #print "dict1['Id']: ", dict1['JName']
    #print  list1
    append = "&cstart="+str(pages)
    url = pubsLink+append
    html_page = urlopener(url)
    if html_page!= False:
        soup = BeautifulSoup(html_page)
        td_list = []
        global count
        table = soup.find('table', {'id': 'gs_cit_list_table'})
        for row in table.findAll("tr"):
            # print row.text
            td_list = row.findAll("td")
            if (td_list.__len__() > 0 ):
                if any(x in td_list[2].text for x in year):
                    selfcites_count = 0
                    #print td_list[1].text
                    authors = (td_list[0].find("span", attrs={"class": "gs_authors"})).text
                    citesLink = (td_list[1].find("a")).get('href')
                    citesCount = int(td_list[1].text)
                    #print authors.textt, citesLink
                    #process the record, else ignore
                    dict1 = {'Id': count, 'JName': jName, 'Authors_name': authors, 'YearOfPub':td_list[2].text, 'CitedByLink': citesLink, 'CitesPerPaper':citesCount, 'SelCitesPerPaper':-1};
                    JInfo.append(dict1)           
                    count = count+1
                    writeToFile("https://scholar.google.com/"+citesLink+"\n" )
                    #for this paper review the citated papers and compute self citations
                    for pages in range(0, citesCount, 20):
                        #controlling the blocking of the program
                        global stopat1000
                        checkForDwnldThreshold()
                        stopat1000 = stopat1000 + pages
          
                        Link = citesLink + "&cstart=" + str(pages)
                        selfcites_count = selfcites_count +  computeSelfcites(Link, authors, citesCount)
                        writeToFile(Link)
                    dict1['SelCitesPerPaper'] = selfcites_count     
                    
                    #writeToSpreadsheet(dict1)
                    writeToFile (dict1)
        
    #print JInfo  
      
#function to extract and check the self citations per paper
def computeSelfcites(citesLink, authorNames, citesCount):
    selfcites = 0
    # wait random time then download object
    sleep(choice(r))
    url = "https://scholar.google.com"+citesLink
    html_page = urlopener(url)
    if html_page != False:
        soup = BeautifulSoup(html_page)
        table = soup.find('table', {'id': 'gs_cit_list_table'})
        for row in table.findAll("tr"):
            # print row.text
            td_list = row.findAll("td")
            if (td_list.__len__() > 0 ):
                if any(x in td_list[1].text for x in year):
                    #print td_list[1].text
                    authors = (td_list[0].find("span", attrs={"class": "gs_authors"})).text
                    #print authors, td_list[1].text
                    list1 = authors.split(",")
                    list2 = authorNames.split(",")
                    #print list1, list2
                    check = compareToauthors(list1, list2 )
                    if check == True:
                        selfcites = selfcites + 1
    
    #print selfcites
    # close urllib object
    #html_page.close()
    return selfcites            

def compareToauthors(list1, list2 ):
    
    list1 = [element.upper() for element in list1]
    list2 = [element.upper() for element in list2]
    #print list1, list2
    check = ' '.join(list(set(list1) & set(list2)))
    if check.__len__() > 0:
        #print check
        writeToFile("\n"+str(1)+"\n")
        return True
    return False

#--------------Main Function----------
#read the names one by one from the JournalList file and print it
#readFile.readConfig()
#s = readFile.ReadJName()  
    
#for testing 
s = "3D Research" #"ACM Computing Surveys"#"AAAI Conference on Artificial Intelligence"#"ACM Transactions on Computational Logic" #"ACM Transactions on Applied Perception" #"ACM Transactions on Autonomous and Adaptive Systems" #"ACM Computing Surveys" #"ACM Transactions on Applied Perception" #"4OR" #"ACM Communications in Computer Algebra" 
journalName = s.replace(" ", "+")
start = "------------------" + s + "-----------------\n"
writeToFile(start)
#NOTE: init all the global variables after printing data to file
#print journalName
pubsForjNameURL = getLinktoAllPapers(journalName) #when the JOURNAL name is searched in search box
pages = 0
stopat1000 = stopat1000 + h5_index
writeToFile( str(h5_index) )
totPages = h5_index
for pages in range(0, totPages, 20):
    sys.stdout = orig_stdout
    checkForDwnldThreshold()
    stopat1000 = stopat1000 + pages
    getPubInfo(pubsForjNameURL, journalName, pages) #PAGING logic
    writeToFile( str(pages)+"\n" )
writeToFile( str(JInfo)+"\n" )
writeToSpreadsheet(JInfo)
sys.stdout = orig_stdout
f.close()

# Global List: A list of dictionary elements with SerialNum:<count>,Journal Name:<name of journal>, Authors_name:<name>, YearOfPub:<year>, CitedByLink:<string>, CitesPerPaper:<count>, SelCitesPerPaper:<count>
# --function to extract and check the self citations per paper---
# List per Jounral:A list of following elements for each of the papers in it
# dictionary elements with SerialNum:<count>, Authors_name:<name>, YearOfPub:<year>, CitedByLink:<string>, CitesPerPaper:<count>, SelCitesPerPaper:<count>.
# if year not between 2011 and 2015 then ignore
# else add the count  

# add logic to stop crawling at 2500 for a day and then start further after 24 hrs.






