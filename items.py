# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class StudyItem(Item):
	name = Field()
	description = Field() 

class DisciplineItem(Item):
	name = Field()
	study = Field()

class MajorItem(Item):
	name = Field()
	description = Field()
	discipline = Field()
	university = Field()

class UniversityItem(Item):
	name = Field()
	abbrev = Field()

class ArticulationItem(Item):
	comcollege = Field()
	major = Field()
	major_descr = Field()
	university = Field()
	link = Field()

	
	




