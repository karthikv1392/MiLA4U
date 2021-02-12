class Goal_Parser():
    def __init__(self):
        self.goal_file = "goal_text"
        self.goal_list = ["parking_reccommendation","weather_service","booking_service","availability" ]
        self.goal_string_to_goal_map = {
            "weather_checking" : "1",
            "parking_recommendation" : "0",
            "ticket_availability" : "3",
            "event_booking" : "2"
        }


    def goal_type_identifier(self,goal_text):
        # Identify the type of goal first if it is one of, sequence, AND based , OR based or just one
        if "one of" in goal_text:
            return "oneof"
        elif "seq" in goal_text:
            return "seq"
        elif "and" in goal_text:
            # one can write this rule as "AND" and "OR" to identiy if is AND OR based goal
            return "and"
        elif "or" in goal_text:
            return "or"
        else:
            # just one goal
            return "single"


    def goal_string_generator(self,goal_text):

        #print (goal_text)
        goal_type = self.goal_type_identifier(goal_text)
        goal_json = {}
        encoded_goal_string = "" # Encodes goal as a string of integers
        if goal_type == "oneof":
            split_text_list = goal_text.split("[")
            for item in split_text_list:
                #if "]" in item:
                if "]" in item:
                    goal_item_list = item.split("]")
                    #print (goal_item_list[0])

                    goal_list = goal_item_list[0].split(",")
                    for goal in goal_list:
                        goal_key = goal.strip(" ").strip("'").strip("'")
                        goal_int_repres = self.goal_string_to_goal_map[goal_key]
                        encoded_goal_string = encoded_goal_string + goal_int_repres
                    break

        elif goal_type == "seq":
            split_text_list = goal_text.split("[")
            for item in split_text_list:
                # if "]" in item:
                if "]" in item:
                    goal_item_list = item.split("]")
                    #print(goal_item_list[0])

                    goal_list = goal_item_list[0].split(",")
                    for goal in goal_list:
                        goal_key = goal.strip(" ").strip("'").strip("'")
                        goal_int_repres = self.goal_string_to_goal_map[goal_key]
                        encoded_goal_string = encoded_goal_string + goal_int_repres
                    break
        elif goal_type == "or":
            split_text_list = goal_text.split("[")
            for item in split_text_list:
                # if "]" in item:
                if "]" in item:
                    goal_item_list = item.split("]")
                    #print(goal_item_list[0])

                    goal_list = goal_item_list[0].split("or")
                    #print (goal_list)
                    for goal in goal_list:
                        #print (goal)
                        goal_key = goal.strip(" ").strip("'").strip("'")
                        goal_int_repres = self.goal_string_to_goal_map[goal_key]
                        encoded_goal_string = encoded_goal_string + goal_int_repres
                    break

        elif goal_type == "and":
            split_text_list = goal_text.split("[")
            for item in split_text_list:
                # if "]" in item:
                if "]" in item:
                    goal_item_list = item.split("]")
                    #print(goal_item_list[0])

                    goal_list = goal_item_list[0].split("and")
                    #print (goal_list)
                    for goal in goal_list:
                        #print (goal)
                        goal_key = goal.strip(" ").strip("'").strip("'")
                        goal_int_repres = self.goal_string_to_goal_map[goal_key]
                        encoded_goal_string = encoded_goal_string + goal_int_repres
                    break
        elif goal_type == "single":
            split_text_list = goal_text.split(" ")
            #print (split_text_list[2])
            goal_item_list = split_text_list[2].split("rt")
            #print (goal_item_list)
            goal_key = goal_item_list[0].strip(" ").strip("'").strip("'")
            goal_int_repres = self.goal_string_to_goal_map[goal_key]
            encoded_goal_string = encoded_goal_string + goal_int_repres

            #    goal_item_list = item.split("rt")
            #    print (goal_item_list)
            #    break

        #print (goal_text)
        #print (encoded_goal_string)
        goal_json["goal_string"] = encoded_goal_string
        goal_json["goal_type"] = goal_type
        #print (goal_json)
        return goal_json
