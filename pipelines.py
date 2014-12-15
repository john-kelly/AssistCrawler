# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker 

#######################################################################################
from models import db_connect, create_data_table, StudyModel, DisciplineModel,MajorModel,UniversityModel
from models import ArticulationModel,ComCollegeModel,StudyDisciplineModel,DisciplineMajorModel
from items import StudyItem,DisciplineItem,MajorItem,UniversityItem,ArticulationItem
#######################################################################################

from scrapy.exceptions import DropItem
    
def add_dbObject(session,obj):
    try:
        session.add(obj)
    except:
        session.rollback()
        raise
    return None

def commit_db(session):
    try:
        session.commit()
    except:
        session.rollback()
        raise
    return None

class AssistMePipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates table.
        """
        engine = db_connect()
        create_data_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """
        Save items in the database.
        This method is called for every item pipeline component.
        """
        session = self.Session()

        # Below code is rather hacky in the sense that it is extremly domain specific...
        # Code assumes quite a bit about the current state of the database...
        
        # However, I could not think of another means to dynamically create the relations
        # during the scraping process
        if(type(item)==StudyItem):
            
            #Create study if not created
            study_obj = session.query(StudyModel).filter(
                StudyModel.name == item['name']).first()
            if(not study_obj):
                study_obj = StudyModel(
                    name = item['name'],
                    description = item['description']
                )
                add_dbObject(session,study_obj)
                commit_db(session)
            session.close()
            raise DropItem("DROP")

        if(type(item)==DisciplineItem):
            
            #Code assumes study has been created
            study_obj = session.query(StudyModel).filter(
                StudyModel.name == item['study']).first()
            
            #Create discipline if not created
            #Relate discipline to study if not related
            disc_obj = session.query(DisciplineModel).filter(
                DisciplineModel.name == item['name']).first()
            if(not disc_obj):
                disc_obj = DisciplineModel(name=item['name'])
                study_obj.disciplines.append(disc_obj)
                commit_db(session)
            else:
                if(disc_obj not in study_obj.disciplines):
                    study_obj.disciplines.append(disc_obj)
                    commit_db(session)
            
            session.close()
            raise DropItem("DROP")
                

        if(type(item)==MajorItem):
            
            #Code assumes that discipline has been created
            disc_obj=session.query(DisciplineModel).filter(
                DisciplineModel.name == item['discipline']).first()
            
            #Create univerity if not created
            university_obj=session.query(UniversityModel).filter(
                UniversityModel.abbrev==item['university']).first()
            if(not university_obj):
                university_obj = UniversityModel(
                    name="N/A",
                    abbrev=item['university']
                )
            
            #Create major if not created
            #Relate major to university and discipline if not related
            major_obj=session.query(MajorModel).filter(
                MajorModel.name == item['name'],
                MajorModel.university == university_obj).first()
            if(not major_obj):
                major_obj = MajorModel(
                    name=item['name'],
                    description=item['description'],
                    university=university_obj
                )
                disc_obj.majors.append(major_obj)
                commit_db(session)
            else:
                if(major_obj not in disc_obj.majors):
                    disc_obj.majors.append(major_obj)
                    commit_db(session)

            session.close()
            raise DropItem("DROP")
        
        if(type(item)==ArticulationItem):
            
            #Code assumes that university has been created
            university_obj=session.query(UniversityModel).filter(
                UniversityModel.abbrev==item['university']).first()

            #Code assumes that major has been created
            major_obj=session.query(MajorModel).filter(
                MajorModel.name == item['major'],
                MajorModel.university == university_obj).first()

            #Create comcollege if not created
            comcollege_obj = session.query(ComCollegeModel).filter(
                ComCollegeModel.name==item['comcollege']).first()
            if(not comcollege_obj):
                comcollege_obj = ComCollegeModel(name=item['comcollege'])
            
            #Create articulation if not created
            #Relate articulation: many majors to many comcolleges
            articulation = session.query(ArticulationModel).filter(
                ArticulationModel.major==major_obj,
                ArticulationModel.community_college==comcollege_obj).first()
            if(not articulation):                                                       
                articulation = ArticulationModel(
                    major=major_obj,
                    community_college=comcollege_obj,
                    link=item['link']
                )
            else:
                session.close()
                return item
            add_dbObject(session,articulation)
            commit_db(session)
            session.close()
            raise DropItem("DROP")

"""
from items that have already been seen before
ex. use the unique ids of the major,disc,univ,study in order to identify/drop items!

from scrapy.exceptions import DropItem

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found")
        else:
            self.ids_seen.add(item['id'])
            return item

REMEMBER TO ADD NEW PIPELINES TO DB
"""





