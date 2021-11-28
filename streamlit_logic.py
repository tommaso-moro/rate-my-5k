
"""
A class to handle the logic of the streamlit app. Mainly contains custom methods to query the MongoDB and compute the relevant results that should be 
displayed in the front-end. 
"""
class Model():
    def __init__(self, mongo_collection):
        self.mongo_collection = mongo_collection

    def get_percentile(self, slower_runs, faster_runs):
        return round((100-(slower_runs*100/(slower_runs+faster_runs))), 2)

    ## TOTAL STATS ##
    def get_tot_num_running_performances(self):
        return self.mongo_collection.find({}).count()

    def get_tot_num_male_running_performances(self):
        return self.mongo_collection.find({"gender":"Male"}).count()

    def get_tot_num_female_running_performances(self):
        return self.mongo_collection.find({"gender":"Female"}).count()

    def get_tot_num_events(self):
        aggregate = self.mongo_collection.aggregate([{"$group": {"_id": {"event_name": "$event_name","race_date": "$race_date"}}},{"$project": {"_id": 0,"event_name": "$_id.event_name","race_date": "$_id.race_date"}}, {"$count": "num_events"}])
        num_events = 0
        for item in aggregate:
            num_events = item['num_events']
        return num_events

    def get_tot_num_faster_runs(self, time_in_seconds):
        return self.mongo_collection.find({"time_in_seconds": {"$lt": time_in_seconds}}).count()

    def get_tot_num_slower_runs(self, time_in_seconds):
        return self.mongo_collection.find({"time_in_seconds": {"$gt": time_in_seconds}}).count()

    def get_num_faster_runs_by_age(self, time_in_seconds, age):
        return self.mongo_collection.find({"time_in_seconds": {"$lt": time_in_seconds}, "age_group_lower_bound": {"$lte": age}, "age_group_upper_bound": {"$gte": age}}).count()

    def get_num_faster_runs_by_gender(self, time_in_seconds, gender):
        return self.mongo_collection.find({"time_in_seconds": {"$lt": time_in_seconds}, "gender": gender}).count()

    def get_num_faster_runs_by_age_and_gender(self, time_in_seconds, age, gender):
        return self.mongo_collection.find({"time_in_seconds": {"$lt": time_in_seconds}, "age_group_lower_bound": {"$lte": age}, "age_group_upper_bound": {"$gte": age}, "gender": gender}).count()

    def get_num_slower_runs_by_age(self, time_in_seconds, age):
        return self.mongo_collection.find({"time_in_seconds": {"$gt": time_in_seconds}, "age_group_lower_bound": {"$lte": age}, "age_group_upper_bound": {"$gte": age}}).count()

    def get_num_slower_runs_by_gender(self, time_in_seconds, gender):
        return self.mongo_collection.find({"time_in_seconds": {"$gt": time_in_seconds}, "gender": gender}).count()

    def get_num_slower_runs_by_age_and_gender(self, time_in_seconds, age, gender):
        return self.mongo_collection.find({"time_in_seconds": {"$gt": time_in_seconds}, "age_group_lower_bound": {"$lte": age}, "age_group_upper_bound": {"$gte": age}, "gender": gender}).count()

    def get_stats(self, time_in_seconds, age, gender):
        result = {
            "tot_num_faster_runs": self.get_tot_num_faster_runs(time_in_seconds),
            "tot_num_slower_runs": self.get_tot_num_slower_runs(time_in_seconds),
            "num_faster_runs_by_age": self.get_num_faster_runs_by_age(time_in_seconds, age),
            "num_slower_runs_by_age": self.get_num_slower_runs_by_age(time_in_seconds, age),
            "num_faster_runs_by_gender": self.get_num_faster_runs_by_gender(time_in_seconds, gender),
            "num_slower_runs_by_gender": self.get_num_slower_runs_by_gender(time_in_seconds, gender),
            "num_faster_runs_by_age_and_gender": self.get_num_faster_runs_by_age_and_gender(time_in_seconds, age, gender),
            "num_slower_runs_by_age_and_gender": self.get_num_slower_runs_by_age_and_gender(time_in_seconds, age, gender)
        }
        return result

    