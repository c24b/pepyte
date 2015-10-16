#/usr/bin/python3.4 env
#coding: utf-8
from bs4 import BeautifulSoup as bs
import re
import requests
from urllib.parse import urlparse, urljoin
import collections
html_tags = re.compile("\s(.*?)=?\"(.*?)\"")

open_tag = re.compile("<.*?>")
classes = "(?P<id>.*?)=\"(?P<value>.*?)\""
tags = re.compile("<(/)?(?P<tag>.*?)((\s|\n|\t).*?)?>")
ids = re.compile("(\s|\t|\n)(?P<id>.*?)=?\"(?P<value>.*?)\"")

SPACES = re.compile("\s|\t|\n")
ESPACES = re.compile("^\s|^\t|^\n|\t$|\s$|\n$")
MULTISPACES = re.compile("\s\s+")

class MethodException(Exception):
    pass
        
class ScrapperException(Exception):
    pass

    
    
class Scrapper(object):
    def __init__(self, project_name):
        self.source = None
        self.soup = None
        self.project_name = project_name
    
    def __format__(self):
        #print(self.soup.findAll("span"))
        if self.has_source():
            
            #ici les tags a plat
            tag_list = [n.group('tag') for n in re.finditer(tags, self.doc) if n is not None and not n.group('tag').startswith('!--') and n.group('tag') != 'script']
            counter= collections.Counter(tag_list)
            
            commons_tags = {n[0]:n[1] for n in counter.most_common(20)}
            #Les 20 tags les plus utilisé dans la page
            tag_top_list = sorted(commons_tags, key=commons_tags.get(1))
            tags_dict = collections.defaultdict.fromkeys(tag_top_list, [])
            for tag in tag_top_list:
                for html_chunk in self.soup.findAll(tag):
                    open_t = re.match(open_tag, str(html_chunk))
                    open_t =  re.sub("<"+tag+" ", "",str(open_t))
                    test = [n for n in re.findall(classes, str(open_t)) if n is not None]
                    print(test[0])
                        
                    
            
                        #tags_dict[tag] = [[n.group('id'),n.group('value')] for n in re.finditer(ids, str(html_chunk))]
                        #print(tag, tags_dict[tag])
            #~ for t, v in tags_dict.items():
                #~ counter= [collections.Counter([n[0] for n in v]), collections.Counter([n[1] for n in v])]
                #~ print(t, counter)
                        #~ counter1= collections.Counter([n[0] for n in tags_dict[tag]])
                        #~ print(tag, counter1.most_common(1))
                        #~ counter2= collections.Counter([n[1] for n in tags_dict[tag]])
                        #~ print(tag, counter2.most_common(1))
                        #data = [{n.group('id'): n.group('value')} )]
                    #data = [n for n in data if n != (None, None)]
                
                
                
                #get_list = [(n.group('id'), n.group('value')) for n in re.finditer(ids, self.doc) if (n.group('id'), n.group('value'))!=(None,None)]
                #print(get_list)
        else:
            print("pass")
        #if (n.group(1),n.group(2))!=(None,None)
        #print(tag_list, get_list)
        
            return 
            
    def has_source(self):        
        '''Verify if source has been parsed'''
        if self.source is None:
        
            raise ScrapperException(self.__doc__)
        if self.soup is None:
            raise ScrapperException(self.__doc__)
        return True
    
    def download(self, url):
        r = requests.get(url)
        try:
            self.doc = r.text
            self.soup = bs(self.doc, "lxml")
            return self.doc
        except:
            print(r)
            
    def read(self, full_path):
        with open(full_path, 'r') as f:
            self.doc = f.read()
            self.soup = bs(self.doc, "lxml")
            return self.soup
                
    def get(self, **kwargs):
        '''method to download from an url or load from a file that takes (url ^ doc ^ full_path) as mandatory argument'''
        for k,v in kwargs.items():
            
            if k in ["url", "full_path", "doc"]:
                self.source = v
                
                if k == "url":
                    return self.download(self.source)
                else:
                    return self.read(self.source)
            elif k == "lang":
                self.lang = v
        else:
            raise MethodException

    def __formatxpr__(self, tag_html='''<a target="_blank" href="https://twitter.com/Marmiton_org" onclick="recordInternalLinkGA('Reseaux sociaux', 'Twitter', document.location.href);" class="m_header_twitter" id="ctl00_m_CtrlNavigation_m_hTwitter"></a>'''):
        if tag_html == "" or tag_html == None:
            return (tag_html, None)
        tag_full = re.split(" ", tag_html)
        #~ print(tag_full)
        try:
            target_tag = re.split("<", tag_full[0])[1]
        except IndexError:
            target_tag = tag_full
        target_dict = {n.group(1):n.group(2) for n in re.finditer(html_tags, tag_html) if n is not None}
        return (target_tag, target_dict)
    
    def __filter_xpr__(self, tag_html):
        '''filtering with usual pattern id, class, name '''
        if tag_html == "" or tag_html == None:
            return (tag_html, None)
        target_tag, target_dict = self.__formatxpr__(tag_html)
        target_dict = { k:v for k,v in target_dict.items() if k in ["id", "class", "name"]}
        return(target_tag, target_dict)
    
    
    def clean_spaces(self, value):
        value = re.sub(SPACES," ", value)
        value = re.sub(MULTISPACES," ", value)
        value = re.sub(ESPACES,"", value)
        return value
        
    def get_title(self):
        ''' get_title required the source to be parse'''        
        if self.has_source():
            if self.soup.head.title.text != "":
                self.title = self.soup.head.title.text
            else:
                self.title = self.soup.h1.text
            self.xtitle = self.clean_spaces(self.title)
            return self.xtitle
    
    def get_meta(self):
        if self.has_source():
            self.xmeta = []
            for n in self.soup.findAll('meta'):
                self.xmeta.append(self.__formatxpr__(str(n))[1])
            return self.xmeta
    
    def extract(self, **options):
        '''extract'''
        self.has_source()
        self.multi = True
        self.text = True
        for k,v in options.items():
            if k not in ["multi", "text"]:
               
               tag, html_tag = self.__filter_xpr__(v)
               target_name = k
            else:
                setattr(self,k, v)
        
        if self.multi: 
            if html_tag is None:
                result = self.soup.findAll(tag)
            else:
                result = self.soup.findAll(tag, html_tag)
            if self.text: 
                result = [self.clean_spaces(n.text) for n in result]
            
        else:
            if html_tag is None:
                result = self.soup.findAll(tag)
            result = self.soup.find(tag, html_tag)
            if self.text:
                result = self.clean_spaces(result.text)
        #setattr(self, target_name, result)
        setattr(self, "x"+target_name, result)
        return result
    
    def get_inline(self, name ="data", html_tag='span', inline_value="class", multi=True, text=False):
        '''method to extract value inside a tag'''
        xpr = self.__formatxpr__(html_tag)
        results = []
        for n in self.soup.find_all(xpr[0]):
            if multi:
                try:
                    results.append(n.get(str(inline_value)))
                except:
                    continue
            else:
                results.append(n.get(str(inline_value))[0])
        #~ for link in soup.find_all('a'):
            #~ print(link.get('href'))
        setattr(self, "x"+name, results)
        return results
    def detect_html_pattern(self, html_tag="div"):
        '''detect the more productive inline_tag for type detection
        id_pattern or class_pattern'''
        for n in self.soup.find_all(html_tag):
            print(self.__formatxpr__(str(n)))
            #print([(k, v) for k, v in n.__dict__.items()])
        
        
    def export(self):
        '''export all extracted results in a dict'''
        self.xsources = self.source
        return {re.sub("x", "", k):v for k,v in self.__dict__.items() if k.startswith("x")}
    
    def store_results(self):
        '''store into a specific format CSV TSV JSON, DB'''
        raise NotImplementedError
        
    def get_links(self, html_tag='<a class="texte">'):
        '''extract links'''
        if self.has_source():
            tag, html_tag = self.__filter_xpr__(html_tag)
            if html_tag is None or html_tag == "":
                results = self.soup.findAll(tag)
            else:
                results = self.soup.findAll(tag, html_tag)
            
            res = []
            for n in results:
                n = n.get("href")
                if urlparse(n).scheme== "" or urlparse(n).netloc == "":
                    n  = urljoin(self.source, n)
                res.append(n)
                
            #print([(k, v) for k,v in  uparsed if k in ["scheme", "netloc"]])
            setattr(self, "xlinks", res)
            return res
            

if __name__ == "__main__":
    s = Scrapper("lemonde")
    s.get(url="http://www.lemonde.fr/", lang="fr")
    #~ for n in s.get_inline(html_tag= "span", inline_value="class", multi=True):
        #~ if n is not None:
            #~ for i in n:
                #~ print(i, s.extract(i='<span class="'+i+'">', multi=True, text=True)) 
                #~ break
            #~ break
        #~ break
    s.get(url="http://www.lemonde.fr/", lang="fr")
    s.__format__()
    #s.detect_html_pattern("div")
    #~ s.get_links('<a class="texte">')
    #~ s.get_title()
    #~ s.extract(comments='<div class="comment-body">', multi=True, text=False)
    #~ print(s.export())
    
        

