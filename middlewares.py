from AssistMe.settings import USER_AGENT_LIST
import random
from scrapy import log


"""
Seems to be working. 
However:
Does this run for each request or each crawl?
	I believe request. Need to test
"""
class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        if hasattr(spider,'user_agent'):
        	request.headers['User-Agent'] = spider.user_agent
        else:
        	ua = random.choice(USER_AGENT_LIST)
        	request.headers['User-Agent'] = ua
