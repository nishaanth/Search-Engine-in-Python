import urllib2
import re
import urlparse


# function which crawls the web given the seed
def crawl_seed(seed):
    toCrawl = [seed]
    crawled = []
    index ={} # index for the search engine
    graph ={} # graph used by the page ranking algorithm
    rank ={}  # ranking score evaluated by the page ranker

    while toCrawl:
        page = toCrawl.pop()
        content = get_page(page)

        # if the page times out
        if content == "":
            continue

        # index the page
        add_page_index(index,page,content)

        # get all the outgoing links
        outlinks = get_all_links(content)

        # graph has both the outgoing and incoming links for each node
        if not graph.get(page):
            graph[page]=[],[]

        for links in outlinks:
            graph[page][0].append(links)

        #update for all the incoming links    
        update_graph(page,outlinks,graph)

        #update the crawl list
        union(outlinks,toCrawl)
        crawled.append(page)

    #compute the rank
    rank = compute_rank(graph)


# gets all the links from a page
def get_all_links(content):

    start =0
    result =[]
    while 1:
        url,starting = gen_next_target(content[start:])

        if not url:
            break
        start = starting
        result.append(url)
    return result

# used by get links , generates the next link target
def gen_next_target(content):
    start_link = content.find('<a href')

    if start_link == -1:
        return None

    start_quote = content.find('"',start_link)
    end_quote = content.find('"',start_link+1)
    link = content[start_quote+1:end_quote]

    return link,end_quote

# updates the incoming link structure of the graph
def update_graph(page,outlinks,graph):

    for link in outlinks:
        if graph.get(link):
            graph[link][1].append(page)
        else:
            graph[link] = [],[]
            graph[link][1].append(page)
        
# computes the page rank for all the pages of the corpus
def compute_rank(graph):

    num_loops = 10 #number of time steps
    rank ={}  #rank of the previous iteration
    damp = 0.8 #dampening fator
    n = len(graph) #number of nodes


    # initialize the rank with equi-probability
    for url,links in graph.iteritems():
        rank[url] = 1.0/n

    # iterate over a certain number of time steps         
    for i in range(0,num_loops):
        new_rank ={} #rank of the current time step

        # compute the similarity from this time step
        for url,links in graph.iteritems():
        
            new_rank[url] = (1.0 - d)/n # random walk probability
            popularity =0.0

            # obtain the popularity of its neigbours
            for link in links[1]:
                popularity = popularity + rank[link]/len(graph[link][0])
            popularity = damp * popularity
            new_rank[url] = new_rank[url] + popularity

        # replace the previous rank with the current rank value
        for url,val in rank.iteritems():
            rank[url]= new_rank[url]
    return new_rank


# retrives the contents of a url
def get_page(url):

    try:
        return urllib2.urlopen(url).read()
    except:
        return ""

# builds the index of the search engine
def add_page_index(index,page,content):
    

# gives the union of 2 lists
def union(outlinks,toCrawl):
    for link in outlinks:
        if toCrawl.find(link)==-1:
            toCrawl.append(link)
