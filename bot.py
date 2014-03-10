import praw
import configparser
import textwrap
import http.client
import html.parser
from time import sleep
from random import randint
##I would like to thank /u/umbrae for his help and his source code for
## his bot on /u/serendipity

class BashOrgBot(object):
    def __init__(self):
        #Read config file
        self._read_config()
        
        #Variables for praw
        self.login_user = self.config['user']['login_user']
        self.login_pass = self.config['user']['login_pass']
        self.user_agent = self.config['user']['user_agent']
        self.is_random = True if self.config['user']['mode'] == 'random' else False
        self.time = int(self.config['user']['time_for_list_submit'])
        
        #Variables for getting html
        self.url = 'bash.org'
        
        
        #Setup praw for later
        self.setup_praw()

        #Get list of previously submitted numbers to avoid doubles
        self.wiki_page = self._read_wiki()
        #Data from bash.org in form of quotes[quote_position][quote, refnum, upvotes/downvotes]
        #And submit it
        if self.is_random == True:
            self.quotes = self.return_random_data()
            self._submit_post(self.quotes[0], self.quotes[1], self.quotes[2])
        else:
            self.quotes = self.return_latest_data()
            self.submit_list(self.time)

      
            
                              
        
        
        #self.submit_post(self.quote0, self.ref0, self.upvotes0)
    def _read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
    def setup_praw(self):
        self.r = praw.Reddit(user_agent=self.user_agent)
        self.r.login(self.login_user, self.login_pass)
        
    def submit_list(self, time):
        for i in range(0, len(self.quotes)):
            if self.check_if_submitted(self.quotes[i][1]) != True:
                self._submit_post(self.quotes[i][0], self.quotes[i][1], self.quotes[i][2])
                print('Post submitted successfully!')
                print('Waiting %s minutes...' %str(self.time))
                sleep(time*60)
                       
    def check_if_submitted(self, ref_num):
        if ref_num[1:] in self.wiki_page:
            return True
        else:
            return False
        
    def return_latest_data(self):
        destination = '/?latest'
        cutpoint = '<p class="quote">'

        #init HTMLParser
        h = html.parser.HTMLParser()

        #Download HTML page and make it workable
        conn = http.client.HTTPConnection(self.url)
        conn.request("GET", destination) #Get the info
        res = conn.getresponse()
        data = str(res.read(), 'ascii').split(cutpoint) #Read data and cut it into bits
        del data[0] #cut off banner html on top of page
        data[-1] = data[-1][:data[-1].find('</td')] #There's some more html at the bottom, cutting it off

        #Make some functions to condense code a bit:
        #Cut string between points by finding first part and ending with a number
        sortquote = lambda listx, x, y: listx[listx.find(x)+len(x):y]
        #Pull all info between two substrings
        sortrest = lambda listx, x, y: listx[listx.find(x)+len(x):listx.find(y)] 

        #Get all the quotes, reference numbers, upvotes in list
        quotes = []
        
        for i in range(0, len(data)):
            holdquote = sortquote(data[i], '</a></p><p class="qt">', -5)
            holdquote = h.unescape(holdquote) #convert HTML parts to special characters
            holdquote = holdquote.replace('<br />', '\n  ')

            #Get reference numbers
            holdref = sortrest(data[i], '<b>', '</b>')
            
            #Get upvotes / downvotes
            holdnum = sortrest(data[i], '</a>(', ')<a href=')
            if holdnum[0] != '-':
                holdnum = '+' + holdnum
        
            quotes.append((holdquote, holdref, holdnum))
        return quotes

    
    def return_random_data(self):
        #init HTMLParser
        #print('started random data')
        h = html.parser.HTMLParser()
        
            
        ran_des = '/?random'
        #Download HTML page and make it workable
        conn = http.client.HTTPConnection(self.url)
        conn.request("GET", ran_des) #Get the info
        res = conn.getresponse()
        data = str(res.read(), 'ascii').split('<p class="quote">')
        del data[0]
        #We only need one quote, pick a random one
        single_quote = data[randint(0, len(data))]
        #Cut string between points by finding first part and ending with a number
        sortquote = lambda listx, x, y: listx[listx.find(x)+len(x):y]
        #Pull all info between two substrings
        sortrest = lambda listx, x, y: listx[listx.find(x)+len(x):listx.find(y)] 

        #Grab quote and format it
        holdquote = sortquote(single_quote, '</a></p><p class="qt">', -5)
        holdquote = h.unescape(holdquote) #convert HTML parts to special characters
        holdquote = holdquote.replace('<br />', '\n  ')

        #Get reference number
        holdref = sortrest(single_quote, '<b>', '</b>')

        #Check if we've already used that quote
        #If so redo everything
        if self.check_if_submitted(holdref) == True:
            self.return_random_data()

        #Get upvotes / downvotes
        holdnum = sortrest(single_quote, '</a>(', ')<a href=')
        if holdnum[0] != '-':
            holdnum = '+' + holdnum
        
        quote = [holdquote, holdref, holdnum]
        return quote
    
    def _read_wiki(self):
        #Convert string of numbers seperated by commas and spaces into a list of numbers (as str)
        wiki_page = self.r.get_wiki_page('BashDotOrg', 'index').content_md.replace(' ', '').split(',')
        return wiki_page
    
    def _write_wiki(self, ref_num):
        #Convert list of numbers into a string
        full_list = self.wiki_page
        full_list.append(ref_num[1:])
        join_list = ', '.join(full_list)
        self.r.edit_wiki_page('BashDotOrg', 'index', join_list)
        
    def _submit_post(self, quote, ref_num, upvotes):
        quotetext = quote[:quote.find('\n')]
        if len(quotetext) >= 97:
            quotetext = textwrap.wrap(quotetext, 100)[0]+'...'
        else:
            quotetext = quotetext + '  '
        bodytext = quote + '  \n  [Source](http://bash.org/?%s' % (ref_num[1:]+')')
        title = "%s %s (%s)" % (ref_num, quotetext, upvotes)

        #Submit thread
        self.r.submit('BashDotOrg', title, bodytext)
        #Record quote in wiki
        self._write_wiki(ref_num)
        
    

