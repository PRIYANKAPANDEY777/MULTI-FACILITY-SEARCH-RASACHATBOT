# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import sqlite3,re,os,json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,AllSlotsReset
from rasa_sdk.forms import FormAction
#
#
def rank(facility_type,row_name,rating,detail,location):
    rank=0
    temp=facility_type.split(" ")
    for i in temp:
        if i in row_name:
            rank=rank+1
        if i in detail:
            rank=rank+1
        if i in location:
            rank=rank+1
    return rank



class ActionHelloWorld(Action):
#
    def name(self) -> Text:
        return "action_find_address"
#
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            location=tracker.get_slot("location")
            facility_type=tracker.get_slot('facility')
            print(facility_type,location)
            conn=sqlite3.connect('pincode_data.db')
            curr=conn.cursor()
            if re.search(r'[0-9]{6}',location)!=None:
                pin_code=location

            else:
                curr.execute("SELECT * FROM data where taluka = '{}' or district = '{}' or state = '{}'".format(location,location,location))
                a=curr.fetchall()
                pin_code=''
                for row in a:
                    pin_code=str(row[1])
            dispatcher.utter_message(text="finding for pin_code :{}".format(pin_code))
            all_files=os.listdir('./new_bot_data/')
            if pin_code+'.json' not in all_files:
                dispatcher.utter_message(text="The pincode: {} information isnt currently available".format(pin_code))
            else:
                with open('new_bot_data/'+pin_code+'.json','r') as file:
                    j_data=file.read()
                    try:
                        temp_dict=json.loads(j_data)
                    except:
                        print("File {} cant be opened".format(file))

                    else:
                        data=temp_dict['data']
                        result=[]
                        for row in data:
                            temp=[]
                            if re.search(r'.*'+facility_type+'.*',row['detail'])!=None or re.search(r'.*'+facility_type+'.*',row['location'])!=None or re.search(r'.*'+facility_type+'.*',row['name'])!=None:
                                row_name=str(row['name'].encode('utf-8'))
                                rating=str(row['rating'].encode('utf-8'))
                                detail=str(row['detail'].encode('utf-8'))
                                location=str(row['location'].encode('utf-8'))
                                opens=str(row['open_at'].encode('utf-8'))
                                phone_no=str(row["phone"].encode('utf-8'))
                                temp.append(row_name)
                                temp.append(rating)
                                temp.append(detail)
                                temp.append(location)
                                temp.append(opens)
                                temp.append(phone_no)
                                temp.append(rank(facility_type,row_name,rating,detail,location))
                                result.append(temp)
                    result=sorted(result,key=lambda x: x[-1],reverse=True)
                    count=0
                    for  i in result:
                        if count>3:break
                        count=count+1
                        dispatcher.utter_message(text="name: {},\nrating:{}, score:{}".format(i[0],i[1],i[-1]))
            return []

class ActionSlotReset(Action):
    def name(self):
        return 'action_slot_reset'
    def run(self, dispatcher, tracker, domain):
        return[AllSlotsReset()]

class FacilityForm(FormAction):
    """Custom form action to fill all slots required to find specific type
    of healthcare facilities in a certain city or zip code."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "facility_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["facility_type", "location"]

    def slot_mappings(self) -> Dict[Text, Any]:
        return {"facility": self.from_entity(entity="facility",
                                                  intent=["inform",
                                                          "clinic_finder"]),
                "location": self.from_entity(entity="location",
                                             intent=["location",
                                                     "clinic_finder"])}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]
               ) -> List[Dict]:
        """Once required slots are filled, print buttons for found facilities"""

        location = tracker.get_slot('location')
        facility_type = tracker.get_slot('facility')



        return []
