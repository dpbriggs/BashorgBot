import http.client
import html.parser


def returndata(url, destination, cutpoint):

    h = html.parser.HTMLParser()
    
    conn = http.client.HTTPConnection(url)
    conn.request("GET", destination) #Get the info
    res = conn.getresponse()
    data = str(res.read(), 'ascii').split(cutpoint) #Read data and cut it into bits
    del data[0] #cut off banner crap on top of page
    data[-1] = data[-1][:data[-1].find('</td')] #There's some more crap html at the bottom, cutting it off
    sortquote = lambda listx, x, y: listx[listx.find(x)+len(x):y] #Cut string between points by finding first part and ending with a number
    sortrest = lambda listx, x, y: listx[listx.find(x)+len(x):listx.find(y)] #Pull all info between two substrings
    #Get all the quotes, reference numbers, upvotes
    quotes = []
    
    for i in range(0, len(data)):
        #hold = data[i][data[i].find('</a></p><p class="qt">')+len('</a></p><p class="qt">'):-6]
        holdquote = sortquote(data[i], '</a></p><p class="qt">', -5)
        holdquote = h.unescape(holdquote)
        #quotes.append(hold)
        #print(hold)
        #print("#############")
        #print("")
        #print("#############")

        #Get reference numbers
        holdref = sortrest(data[i], '<b>', '</b>')
        
        #Get upvotes / downvotes
        holdnum = sortrest(data[i], '</a>(', ')<a href=')
        if holdnum[0] != '-':
            holdnum = '+' + holdnum
        



        quotes.append((holdquote, holdref, holdnum))
                      
    return quotes

   

    
url = 'bash.org'
destination = '/?latest'
cutpoint = '<p class="quote">'
test = returndata(url, destination, cutpoint)
print(test[0][0])
print("####")
print(test[11][1])
print("####")
print(test[11][2])
#print("##########")
#print("")
#print(test[1])
