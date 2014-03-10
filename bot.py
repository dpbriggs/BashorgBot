import praw
import configparser
import textwrap
import http.client
import html.parser


class BashOrgBot(object):
    def __init__(self):
        #Read config file
        self._read_config()

        #Variables for praw
        self.login_user = self.config['user']['login_user']
        self.login_pass = self.config['user']['login_pass']
        self.user_agent = self.config['user']['user_agent']
        
        #Variables for getting html
        self.url = 'bash.org'
        self.destination = '/?latest'
        self.cutpoint = '<p class="quote">'
        
        #Setup praw for later
        self.setup_praw()

        #Data from bash.org in form of quotes[quote_position][quote, refnum, upvotes/downvotes]
        self.quotes = self.return_data(self.url, self.destination, self.cutpoint)
        

        #First quote stuff (for testing purposes)
        self.quote0 = self.quotes[45][0]
        self.ref0 = self.quotes[45][1]
        self.upvotes0 = self.quotes[45][2]
        print(self.quote0)
        print(self.ref0)
        print(self.upvotes0)
        
    def _read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
    def setup_praw(self):
        self.r = praw.Reddit(user_agent=self.user_agent)
        self.r.login(self.login_user, self.login_pass)
        

    def return_data(self, url, destination, cutpoint):
        #init HTMLParser
        h = html.parser.HTMLParser()

        #Download HTML page and make it workable
        conn = http.client.HTTPConnection(url)
        conn.request("GET", destination) #Get the info
        res = conn.getresponse()
        data = str(res.read(), 'ascii').split(cutpoint) #Read data and cut it into bits
        del data[0] #cut off banner html on top of page
        data[-1] = data[-1][:data[-1].find('</td')] #There's some more html at the bottom, cutting it off

        #Make some functions to condense code a bit
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
    
    
    def submit_post(self, quote, refnum, upvotes):
        quotetext = textwrap.wrap(quote, 100)[0]+'...'
        
        title = "%s %s (%s)" % (refnum, quotetext, upvotes)
        ##I haven't yet added the code to submit, I've done that in a terminal
        ##This is what it would look like:
        #r.submit('BashDotOrg', 'test post 3 please ignore', url='http://bash.org/?400459', raise_captcha_exception=True)
        #
        ##Which has only raised the: "Would you like to try that again?" error
    def hi(self):
        print('hi')
BashOrgBot()

    

