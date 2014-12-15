##############################
# This spider is designed to #
# scrape a single community  #
# college                    #
##############################

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request
from scrapy import log

#from scrapy.shell import inspect_response
#inspect_response(response)

# could probaly change this to *
from AssistMe.items import StudyItem,DisciplineItem,MajorItem,UniversityItem,ArticulationItem

class StudySpider(Spider):
    name = "relational"
    allowed_domains = ['assist.org']
    start_urls = ['http://www2.assist.org/exploring-majors/browseAreas.do']

    def start_requests(self):
        return [Request(url=self.start_urls[0],
                        callback=self.parse_browse)]

    def parse_browse(self,response):         
        sel_options = response.xpath('//select[@name="areaId"]/option')
        study_form_requests = []        
        
        for sel in sel_options[1::]:
            study = sel.xpath('text()').extract()[0] 
            areaId = sel.xpath('@value').extract()[0]
            study_form_request = FormRequest(
                url='http://www2.assist.org/exploring-majors/findAreaOfStudyOverview.do',
                formdata={'areaId':str(areaId)}, 
                callback=self.parse_study)
            study_form_request.meta['study'] = study
            study_form_request.meta['areaId'] = areaId
            study_form_requests.append(study_form_request)
        return study_form_requests
    
    def parse_study(self,response):               
        study = response.meta['study']
        areaId = response.meta['areaId']
        
        sel_options = response.xpath('//select[@name="disciplineId"]/option')
        study_desc = response.xpath('//p[@class="tablehead"]/following::p/text()')[0].extract()

        discipline_form_requests = []

        item = StudyItem()
        item['name'] = study
        item['description'] = study_desc

        for sel in sel_options[1::]: 
            discipline = sel.xpath('text()').extract()[0]
            disciplineId = sel.xpath('@value').extract()[0]
            discipline_form_request = FormRequest(
                url='http://www2.assist.org/exploring-majors/findDiscipline.do', 
                formdata={'areaId':str(areaId),
                          'disciplineId':str(disciplineId)},
                callback=self.parse_discipline)
            discipline_form_request.meta['study'] = study
            discipline_form_request.meta['discipline'] = discipline
            discipline_form_requests.append(discipline_form_request)

        return discipline_form_requests + [item]
           

    def parse_discipline(self,response):        
        study = response.meta['study']
        discipline = response.meta['discipline']
        
        hrefs = response.xpath("//@href").re("findMajorDescription\.do.+")
        
        item = DisciplineItem()
        item['name'] = discipline
        item['study'] = study

        major_requests = []
        for href in hrefs:
            major_requset = Request(
                url="http://www2.assist.org/exploring-majors/"+str(href),
                callback=self.parse_major,
                dont_filter=True)
                # dont_filter controls processing duplicate requests
                # set to true in this instance to allow for the process of 
                # ALL paths (for the purpose of relation construction)
            major_requset.meta['study'] = study
            major_requset.meta['discipline'] = discipline
            major_requests.append(major_requset)
        
        return major_requests+[item]  
    
    def parse_major(self,response):
        ######################################################################
        ######################################################################
        # Choose the community college to scrape
        collegeId = '467'
        comcollege = 'Berkeley City College'
        ######################################################################
        ######################################################################
        study = response.meta['study']
        discipline = response.meta['discipline']
        ######################################################################
        # Not exactly sure why these bugs are occuring. In some instances, it 
        # appears that the structure of the data/html varies unexpectedly
        ######################################################################
        abbrev = response.xpath("//form[@name='collegeForm']/input[1]/@value").extract()
        if abbrev:
            abbrev = abbrev[0]
        else:
            abbrev = "BUG"
            return
        
        majorId = response.xpath("//form[@name='collegeForm']/input[2]/@value").extract()
        if majorId:
            majorId = majorId[0]
        else:
            majorId = "BUG"
            return
        
        major = response.xpath("//td[2]/p[1]/text()[2]").extract()
        if major:
            major = ' '.join(major[0].split())
        else:
            major = "BUG"
            return

        major_descr = response.xpath("//td[2]/p[2]/text()").extract()
        if major_descr:
            major_descr = ' '.join(major_descr[0].split())
        else:
            major_descr = "BUG"
            return

        typeId = response.xpath("//form[@name='collegeForm']/input[3]/@value").extract()
        if typeId:
            typeId = typeId[0]
        else:
            typeId = "BUG"
            return
        ######################################################################
        ######################################################################
        commcollege_form_request = FormRequest(
            url='http://www2.assist.org/exploring-majors/findMajorDescription2.do', 
            formdata={'abbrev':str(abbrev),
                    'collegeId':collegeId,
                    'majorId':str(majorId),
                    'type':str(typeId)},
            callback=self.parse_comcollege)
            #dont_filter=True 
        
        item = MajorItem()
        item['name'] = major
        item['description'] = major_descr
        item['discipline'] = discipline
        item['university'] = abbrev

        commcollege_form_request.meta['major'] = major
        commcollege_form_request.meta['university'] = abbrev
        commcollege_form_request.meta['comcollege'] = comcollege
        commcollege_form_request.meta['major_descr'] = major_descr
        
        return [item] + [commcollege_form_request]
    
    def parse_comcollege(self,response):
        href_majorprep = response.xpath("//table[@id='widedata']/tr[2]/td[7]/a/@href").extract()
        if (href_majorprep == []):
            href_majorprep = "NO AGREEMENT"
        else:
            href_majorprep = str(href_majorprep[0])

        item = ArticulationItem()
        item['comcollege'] = response.meta['comcollege']
        item['major'] = response.meta['major']
        item['major_descr'] = response.meta['major_descr']
        item['university'] = response.meta['university']
        item['link'] = href_majorprep

        return [item]

