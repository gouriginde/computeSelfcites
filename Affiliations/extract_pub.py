#program to identify the publisher and get author affiliations
# dictionary is : (J_Name,J_Country, A_Title, A_URL, A_Year, A_Pub,A_Auth1, A_Auth2, A_Auth3, A_Auth1_Aff, A_Auth2_Aff, A_Auth3_Aff, A_SelfCites, A_TotalCites, J_TotalCites, J_SelfCites) 
from BeautifulSoup import BeautifulSoup
from time import sleep
from random import choice
import urllib2
import pprint
import sys
import json
import datetime
import codecs
import json
import re
authorsList = []
AffiliationsList = [] 

#def wrtietoFile(ele):
#    writer = csv.writer(open('dict.csv', 'wb'))
#    for key, value in mydict.items():
#        writer.writerow([key, value])

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

def getAllCitingArticles(articleURL):
    global data
    citingList = []
    #print articleURL
    for i in data: #i is each dictionary element
        if 'A_URL' in i:
            if i['A_URL'] == articleURL:
            #print url
                citingList.append(i)

    
    return citingList

def getAffsSpringer(ArticleEle):
    item = ArticleEle['A_URL']
    #item = "http://link.springer.com/article/10.1007/s00500-010-0591-1"#"http://link.springer.com/article/10.1007/s00500-012-0824-6"
    soup1 = getPageContent(item)
    
    affs = []
    aa = soup1.find('ul', {'class' : "AuthorNames"})
    ab = aa.findAll('li')
    for row in ab:
        auth = (row.find('span', {'class': "AuthorName"})).text
        Aff_tp = row.find('span', {'class': "AuthorsName_affiliation"})
        Aff = (Aff_tp.span).text
        L1 = [auth, Aff]
        affs.append(L1)
        print auth, Aff
        
    ct = 1
    for x in affs:
        ArticleEle.update({'Auth_'+str(ct)+'_Aff':x[1]})
        ct = ct + 1
            
    return ArticleEle

def getAffsACM(ArticleEle):
    item = ArticleEle['A_URL']
    
    #item = "http://dl.acm.org/citation.cfm?id=2168843"#"http://dl.acm.org/citation.cfm?id=2168841" #"http://dl.acm.org/citation.cfm?id=2451146"
    soup1 = getPageContent(item)
    #get the affiliations
    affs = [] #list which stores authname, id, affs in that order
    # get the author names "authorName svAuthor"
    ab = soup1.find('div', {'id' : "divmain"})
    x = ab.table
    tables = x.findAll('table')
    
    bibs = tables[4].findAll("tr")
    tmp =  (bibs[2].find("td")).text
    tml = tmp.replace(";&nbsp;", "")
    dwlnds = tml.split("&middot")
    
    dwn = dwlnds[3].split(":")
    local = dwlnds[4].split(":")
    print dwlnds[3],dwlnds[4],dwn[1]
    ArticleEle.update({'Downloads':dwn[1]})
    ArticleEle.update({'local_cites':local[1]})
    
    for row in tables[1].findAll("tr"):
        detls = row.findAll('td')
        auth = (detls[1].text).encode('utf-8')
        
        print "Auth: " + str(auth)
        if detls[2].text is not None:
            Aff = (detls[2].text).encode('utf-8')
            print "Affs: " + str(Aff)
         
        else:
            affs = "null"
        L1 = [auth, Aff]
        affs.append(L1)
         
          
    print "-------------------------------------------"
     
    ct = 1
    for aa in affs:
        ArticleEle.update({'Auth_'+str(ct)+'_Aff':aa[1]})
        ct = ct + 1
    
    
    return ArticleEle

def getAffsIEEEXplore(ArticleEle):
    return

def getAuthorAffiliations(ArticleEle):
    item = ArticleEle['A_URL']
    if "sciencedirect" in item:
        updatedEle = getAffsScienceDirect(ArticleEle)
        return updatedEle
    elif "springer" in item:
        updatedEle = getAffsSpringer(ArticleEle)
        return updatedEle
    elif "dl.acm" in item:
        updatedEle = getAffsACM(ArticleEle)
        return updatedEle
    elif "ieeexplore" in item:
        updatedEle = getAffsIEEEXplore(ArticleEle)
        return updatedEle
    else:
        return False
    

def getAffsScienceDirect(ArticleEle):
    
    item = ArticleEle['A_URL']
    soup1 = getPageContent(item)
    #add logic here to get check if the article is from springer/ACM or the IEEE
    
    #get the affiliations
    affs = [] #list which stores authname, id, affs in that order
    # get the author names "authorName svAuthor"
    ab = soup1.find('ul', {'class' : "authorGroup noCollab svAuthor"})
    #print ab
    for bb in ab.findAll('li'):
        aa = bb.findAll('a')
        #print aa
        Authname = aa[0].text
        #Id = 'null'
        if len(aa)>1 and (aa[1].get('title') is not None):
        #if aa is not None and len(aa) > 2:
        #if aa[1].has_attr('title'):
            Id = aa[1].get('href')
            #print Id
        #if aa[1].get('title') == None :
        else:
            if len(affs) > 1:
                Id = affs[0][1]
            else:
                Id = 'null'            
        
        L1 = [Authname, Id]
        affs.append(L1)
    
    #print affs    
    
    x = soup1.find('ul', {'class': "affiliation authAffil"})
    #print x
    
    if len(affs) == 1:
        y = x.findAll('span')
        ele =[n.text for n in y]
        #print ele[0]
        affs[0].append(ele[0])
        #print affs
    
    elif (len(affs) == 2) and (affs[1][1] == 'null'):
        y = x.findAll('span')
        ele =[n.text for n in y]
        affs[0].append(ele[0])
        affs[1].append(ele[0])
        #print affs
    
        
    else:
        #print "here"
        for y in x.findAll('li'):
            tp = y.get('id')
            #print tp,y.text
            for z in affs:
                #tp1 = [value for key, value in z.items() if key.startswith('Auth_')]
                #tp2 = [value for key, value in z.items() if key.startswith('id')]
                if str(z[1])[1:] == y.get('id'):
                        ele = y.text
                        z.append(ele)
                        #print z
                elif tp is None:
                    ele = y.text
                    z.append(ele)
                    #print z
    #print "Full n Final Affs"
    #print affs
    for m in affs:
        if m[1] == 'null' and affs[0][1]!='null':
            x = affs[0][2]
            m.append(x)
    
    ct =0
    for m in affs:
        ct = ct +1
        if m[1] == 'null':
            ArticleEle.update({'Auth_'+str(ct)+'_Aff':"god help"})
        else:
            ArticleEle.update({'Auth_'+str(ct)+'_Aff':m[2]})
  
    return ArticleEle

def compareToauthors(list1, list2 ):
    
    list1 = [(element.strip()).upper() for element in list1]
    list2 = [(element.strip()).upper() for element in list2]
    #print list1 
    #print list2
    #print "----------------------------------------"
    check = ' '.join(list(set(list1) & set(list2)))
    if check.__len__() > 0:
        #print "check is : " 
        #print check
        #writeToFile("\n"+str(1)+"\n")
        return True
    return False

def cleanUp(Clist):
    for i in Clist:
        if len(i) < 15:
            Clist.remove(i)
    
    return Clist

def createAuthElements(AList):
    authDict = {}
    ct=1
    #print "List has: " + str(AList)
    for i in AList:
        name = 'Auth_'+str(ct)
        ct  = ct + 1
        authDict[name] = i
          
    return authDict
    

def ComputeSelfCitations(CList):
    #extract A_Authors_names and C_authors from every dictionary item of the CList
    #compare, if match increment the counter, add this counter as a new field
    #print  CList[0]
    #print  CList[0]['A_C_Title']
    #list1 = (CList[0]['A_Authors_names']).split(",")   
    #print list1
    #print "-------------------"
    cleanList = cleanUp(CList)
    print len(cleanList)
    #articleAuth = list1.split(",")
    selfcites = 0 
    for i in cleanList:
        list2 = (i['C_authors']).split(",")
        check = compareToauthors (list1, list2)
        if check == True:
            selfcites = selfcites + 1
    #print "Selfcites = :" + str(selfcites)
    
    #ArticleData = generateDictionaryNode(list1, CList[0], selfcites)
    return selfcites

def getRedirectedUrl(OrigUrl):
    soup = getPageContent(OrigUrl)
    #print soup
    re_direct = (soup.find('script')).text
    extract = re_direct.split("'")
    #print extract
    
    #et = "http://dl.acm.org/citation.cfm?id=2168841"
    return extract[1] # overwrite the existing to actual one
    #return et
    

def generateDictionaryNode(list1,ArticleInfo, selfciteCount ):
    authNameEle = createAuthElements(list1)
    URl = getRedirectedUrl(ArticleInfo['A_URL'])
    URL = URl.replace("\\x3d", "=")
    #create a new dictionary element and return
    dictEle = {'A_Year':ArticleInfo['A_Year'] , 'A_articlePub':ArticleInfo['A_articlePub'] , 
               'A_Title':ArticleInfo['A_Title'], 'A_CitedByLink':ArticleInfo['A_CitedByLink'] ,
               'A_TotalCites':ArticleInfo['A_TotalCites'] , 'J_h5_index':ArticleInfo['J_h5_index'] ,
               'J_venue':ArticleInfo['J_venue'], 'J_h5_median': ArticleInfo['J_h5_median'], 
               'A_URL':URL, 'J_Name':ArticleInfo['J_Name'],
               'A_SelfCites': selfciteCount}
    dictEle.update(authNameEle)
    
    return dictEle

def getPageContent(link):
    html_page = urlopener(link)
    #print html_page
    if html_page!= False: 
        soup = BeautifulSoup(html_page)
        return soup
    return False


data = json.load(open('../dump/ACM european Conference on Computer Systems.txt'))
# Springer: data = json.load(open('../dump/Genetic Programming and Evolvable Machines.txt'))
#data = json.load(open('../dump/Genetic Programming and Evolvable Machines.txt'))
#print data
#print len(data)

AllArticleURLs = []
All_tmpArticleInfo = []
AllArticleInfo = []
#tp = getAffsACM("dummy")
#getAffsSpringer("dummy")

#for every element in the file fetch the article URL into a list        
for i in data: #i is each dictionary element
    if 'A_URL' in i:
        url = i['A_URL']
        #print url
        AllArticleURLs.append(url)
        
print "Total Unique are" + str(len(set(AllArticleURLs)))
print set(AllArticleURLs) 

uniqueList = list(set(AllArticleURLs)) #this set consists of the unique URL's of the articles in a Journal
# for every article extract the list of citing articles
#print uniqueList
for i in uniqueList:
    #i = uniqueList[0]
    #print i
    citingArticles = getAllCitingArticles(i)
    list1 = (citingArticles[0]['A_Authors_names']).split(",")   
    
    #print len(citingArticles)
    #pprint.pprint(citingArticles, width=1)
    #print "-------------------------------------------------------"
    
    self_cites = ComputeSelfCitations (citingArticles)
    #self_cites = 0
    ArticleInfo = generateDictionaryNode(list1, citingArticles[0], self_cites)
    All_tmpArticleInfo.append(ArticleInfo)

print All_tmpArticleInfo
#pprint.pprint(All_tmpArticleInfo, width=1)
#for every article dictionary in the AllArticleInfo, process the URL to scrape the Author affiliations
for m in All_tmpArticleInfo:
    #m  = All_tmpArticleInfo[0]
    Affs_Info = getAuthorAffiliations(m)
    AllArticleInfo.append(Affs_Info)
pprint.pprint(AllArticleInfo, width=1)
    
#print Affs_Info
#add Affs_Info to existing dictionary element

#Print the info of all the articles in a journals
#compute the total citations and self-citations of the Journal by doing just additions
#write the data to a file preff csv file
#do additional check if the country info is available in the already scraped data, if so add the field to the dictionary


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #print "Authors are: " + str(len(authors))
    #print "Affs are : " + str(len(affs))
    #y = ast.literal_eval(i)
    #print i['J_venue'] 
    #print i.keys()
    #print "--------------------------------------------------"
    #x = "{'A_Year': u'2012', 'A_articlePub': u'Applied Soft Computing 12 (3), 1180-1186', 'A_Title': 'Firefly Algorithm for solving non-convex economic dispatch problems with valve loading effect', 'C_CitedDocPubName': u'Evolutionary Computation (CEC), 2013 IEEE Congress on, 621-628', 'C_Title': 'Improved Cultural Immune Systems to Solve the Economic Load Dispatch Problems', 'A_TotalCites': 215, 'C_authors': 'R Goncalves, C Almeida, M Goldbarg, E Goldbarg, M Delgado', 'J_venue': u'https://scholar.google.com//citations?hl=en&view_op=list_hcore&venue=lFUe46cMy-8J.2015', 'J_h5_median': u'93', 'C_year': u'2013', 'A_Authors_names': 'XS Yang, SSS Hosseini, AH Gandomi', 'A_Id': 1, 'C_Link': u'http://scholar.google.com/scholar?oi=bibs&cluster=15834384247775296586&btnI=1&nossl=1&hl=en', 'C_citedId': 57, 'A_CitedByLink': u'/citations?hl=en&venue=lFUe46cMy-8J.2015&view_op=hcore_citedby&hcore_pos=6', 'J_Name': 'Applied+Soft+Computing', 'J_h5_index': u'65'}"
    #y = ast.literal_eval(x)
    #print y.keys() 
    