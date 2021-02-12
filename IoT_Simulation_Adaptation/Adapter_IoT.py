from Custom_Logger import logger
import numpy as np
from numpy import array
import random
import pandas as pd
from ES_Manager import ES_Manager
from datetime import datetime
import time

# The purpose of this class is to implement the adaptation logic depending on the type of adaptation that needs to be executed

# all exits are people counters v1Ex, v2Ex, v3Ex
# all entrances are rfid v1En, v2En, v3En

# parking entrance and exits are in Pxxxx

es_obj = ES_Manager()

class Adaptation_Planner():
    def __init__(self):
        self.dict_sensor_freq_keys = {"v1EnNorm": 20000, "v1EnCrit": 5000, "v1ExNorm": 20000, "v1ExCrit": 5000,
                                "v2EnNorm": 20000, "v2EnCrit": 5000, "v2ExNorm": 20000, "v2ExCrit": 5000,
                                "v3EnNorm": 20000,
                                "v3EnCrit": 5000, "v3ExNorm": 20000, "v3ExCrit": 5000, "p1EnNorm": 60000,
                                "p1EnCrit": 10000, "p1ExNorm": 30000, "p1ExCrit": 10000, "p2EnNorm": 60000,
                                "p2EnCrit": 10000, "p2ExNorm": 30000, "p2ExCrit": 10000}
        self.sensor_id_key_map = {"S34" : "p1En","S33":"p1Ex","S42" : "p2En","S41":"p2Ex","S1":"v1En","S2":"v1Ex","S18":"v2En","S20":"v2Ex","S24":"v3En","S25":"v3Ex"}

        self.sensor_mapping = {'S1': 'S1', 'S11': 'S2', 'S17': 'S3', 'S18': 'S4', 'S2': 'S5', 'S20': 'S6', 'S24': 'S7', 'S25': 'S8', 'S26': 'S9', 'S33': 'S10', 'S34': 'S11', 'S35': 'S12', 'S41': 'S13', 'S42': 'S14', 'S43': 'S15', 'S46': 'S16', 'S47': 'S17', 'S48': 'S18', 'S49': 'S19', 'S50': 'S20', 'S51': 'S21', 'S7': 'S22'}
        self.reverse_sensor_map = {'S1': 'S1', 'S2': 'S11', 'S3': 'S17', 'S4': 'S18', 'S5': 'S2', 'S6': 'S20', 'S7': 'S24', 'S8': 'S25', 'S9': 'S26', 'S10': 'S33', 'S11': 'S34', 'S12': 'S35', 'S13': 'S41', 'S14': 'S42', 'S15': 'S43', 'S16': 'S46', 'S17': 'S47', 'S18': 'S48', 'S19': 'S49', 'S20': 'S50', 'S21': 'S51', 'S22': 'S7'}
        self.sensor_id_list = [] # Integere values just containing the id of the sensors
        for key in self.sensor_id_key_map:
            sensor_id = int(self.sensor_mapping[key].split("S")[1])
            self.sensor_id_list.append(sensor_id)

        # Define the energy thresholds 1.45 and 1.35§§§§§§§§§§§§§§§§§§§§§
        #self.high_power = 14.5
        #self.high_power = 22.05
        self.high_power = 1.45

        #self.base_power = 13.5
        self.base_power = 1.35

        # Define the reduction frequency values
        self.reduction_freq_normal_hp = 20000
        self.reduction_freq_critical_hp = 10000
        self.reduction_freq_normal_bp = 10000
        self.reduction_freq_critical_bp = 5000
        self.adapation_count  = 0   # Keep a count on the total adaptations performed
        self.time_count  = 0 # Keep a check on the time lapsed
        self.bp_time = 0 # If a sensor has stayed in bp for 20 instances reset this value and restore to old frequency
        self.bp_count = 2
        self.arrival_threshold = 60 # adapt if arrival is less than 50
        self.parking_arrival_threshold = 100 # adapt if arrival is less than 50
        self.enabled_keys = []

    def get_decision_plan_from_cloud(self):
        # Fetch the ES data to check what can be the reduction rate
        try:
            res = es_obj.search_es_id(index="arrival_rate",id="iot1")
            print (res)
            for key in res:
                if "parking" in key:
                    if res[key] < self.parking_arrival_threshold:
                        self.enabled_keys.append("p1En")
                        self.enabled_keys.append("p2En")
                        self.enabled_keys.append("p1Ex")
                        self.enabled_keys.append("p2Ex")
                elif "venue" in key:
                    if res[key] < self.arrival_threshold:
                        self.enabled_keys.append("v1En")
                        self.enabled_keys.append("v2En")
                        self.enabled_keys.append("v3En")
                elif "rfid" in key:
                    if res[key] < self.arrival_threshold:
                        self.enabled_keys.append("v1Ex")
                        self.enabled_keys.append("v2Ex")
                        self.enabled_keys.append("v3Ex")

        except Exception as e:
            pass

        return self.enabled_keys

    def reactive(self,in_energy_list):
        # Get the list of energy consumption and decide on the adaptation
        # Change the frequency of sensors in CupCarbon

        # Ignore the index which has not to be accounted for computing the increase

        # Energy list consists of 1 lists with energy of each component
        '''
        energy_list = []
        for index in range(22):
            sum_val = 0
            for i in range (len(in_energy_list)):
                sum_val = sum_val + in_energy_list[i][index]
            energy_list.append(sum_val)

        '''
        max_value  = 0
        max_index = 0
        energy_list = in_energy_list[0]
        #energy_list = in_energy_list
        for index in range(0,len(energy_list)):
            if (index!=20):
                if energy_list[index] > max_value:
                    max_value = energy_list[index]
                    max_index = index
        # Calculate the frequency reduction and write to the text file
        frequency_map = self.dict_sensor_freq_keys.copy()
        # Calculate the data transfer frequency reduction
        total_energy_consumed = sum(energy_list)
        print ("plan")
        logger.info("Inside Adaptation Planner")
        print (total_energy_consumed)



        if total_energy_consumed>= self.high_power:
            enabled_keys = self.get_decision_plan_from_cloud()

            print(enabled_keys)
            for index in self.sensor_id_list:
                reduction_freq_critical = 0
                reduction_freq_normal = 0
                self.adapation_count += 1
                if energy_list[index] == max_value:

                    reduction_freq_normal = self.reduction_freq_normal_hp
                    reduction_freq_critical = self.reduction_freq_critical_hp
                else:
                    reduction_percent = ((max_value - energy_list[index]) / max_value)
                    reduction_freq_normal = int(self.reduction_freq_normal_hp * reduction_percent)
                    reduction_freq_critical = int(self.reduction_freq_critical_hp * reduction_percent)

                sensor_key = "S" + str(index)  # Form the sensor id to be used to get data from the reverse map
                sensor_freq_key = self.sensor_id_key_map[self.reverse_sensor_map[sensor_key]]

                if sensor_freq_key in enabled_keys:
                    frequency_map[sensor_freq_key + "Norm"] = frequency_map[
                                                              sensor_freq_key + "Norm"] + reduction_freq_normal
                    frequency_map[sensor_freq_key + "Crit"] = frequency_map[
                                                              sensor_freq_key + "Crit"] + reduction_freq_critical

            self.enabled_keys = []  # reset to old set
            # Write the adaptation to the file
            write_string = ""
            for key in frequency_map:
                write_string = write_string + key + " " + str(frequency_map[key]) + "\n"
            write_string = write_string[:-1]

            text_file = open("config.txt", "w")
            text_file.write(write_string)
            text_file.close()


        elif total_energy_consumed < self.high_power and total_energy_consumed >= self.base_power:
            self.adapation_count += 1
            enabled_keys = self.get_decision_plan_from_cloud()

            print(enabled_keys)
            for index in self.sensor_id_list:
                reduction_freq_critical = 0
                reduction_freq_normal = 0
                if energy_list[index] == max_value:
                    reduction_freq_normal = self.reduction_freq_normal_bp
                    reduction_freq_critical = self.reduction_freq_critical_bp
                else:
                    reduction_percent = ((max_value - energy_list[index]) / max_value)
                    reduction_freq_normal = int(self.reduction_freq_normal_bp * reduction_percent)
                    reduction_freq_critical = int(self.reduction_freq_critical_bp * reduction_percent)

                sensor_key = "S" + str(index)  # Form the sensor id to be used to get data from the reverse map
                sensor_freq_key = self.sensor_id_key_map[self.reverse_sensor_map[sensor_key]]
                if sensor_freq_key in enabled_keys:
                    frequency_map[sensor_freq_key + "Norm"] = frequency_map[
                                                              sensor_freq_key + "Norm"] + reduction_freq_normal
                    frequency_map[sensor_freq_key + "Crit"] = frequency_map[
                                                              sensor_freq_key + "Crit"] + reduction_freq_critical

            self.enabled_keys = []
            # Write the adaptation to the file
            write_string = ""
            for key in frequency_map:
                write_string = write_string + key + " " + str(frequency_map[key]) + "\n"
            write_string = write_string[:-1]
            text_file = open("config.txt", "w")
            text_file.write(write_string)
            text_file.close()


        elif total_energy_consumed < self.base_power:
            # Means no need to perform any adaptation the original frequency remains as it is
            self.bp_time +=1
            if (self.bp_time>=self.bp_count): # Change this depending on the lag value
                # Restore back to original frequencies
                # Write the adaptation to the file
                write_string = ""
                for key in frequency_map:
                    write_string = write_string + key + " " + str(frequency_map[key]) + "\n"
                write_string = write_string[:-1]
                text_file = open("config.txt", "w")
                text_file.write(write_string)
                text_file.close()

        logger.info("Adaptation reactive executor")


if __name__ == '__main__':
   ada_plan_obj = Adaptation_Planner()
   #start_time = time.time()
   #ada_plan_obj.reactive([[0.2546080000392976, 0.21209760000783717, 1.0735600002917636, 0.8160048001955147, 0.34579200006555766, 0.1873040000355104, 0.7779199998694821, 0.414683200095169, 0.57155760016758, 0.4832416000790545, 1.3014400003376068, 0.23820560004605795, 0.27449920008075424, 1.3814128003577935, 0.13796640000509797, 0.2656368000098155, 0.24916320000920678, 0.07207200000266312, 0.5317488001528545, 0.4250360000805813, 2.3117408000762225, 0.07298720001563197], [0.08644800001638941, 0.030888000001141336, 0.15640640004130546, 0.1202704000279482, 0.08644800001638941, 0.028816000005463138, 0.10135839998474694, 0.04782720001094276, 0.09213120002823416, 0.020191200001136167, 0.2609360000678862, 0.04322400000819471, 0.021612000004097354, 0.06321600001683692, 0.02059200000076089, 0.012355200000456534, 0.04942080000182614, 0.008236800000304356, 0.021612000004097354, 0.021612000004097354, 0.3010960000210616, 0.007677600002352847], [0.03365200000189361, 0.0185328000006848, 0.09157280002546031, 0.06404640001346706, 0.08644800001638941, 0.04322400000819471, 0.09197759998642141, 0.08866240001952974, 0.09213120002823416, 0.020191200001136167, 0.2575040000665467, 0.021612000004097354, 0.0072040000013657846, 0.06321600001683692, 0.010296000000380445, 0.012355200000456534, 0.04942080000182614, 0.014414400000532623, 0.021612000004097354, 0.021612000004097354, 0.2732128000170633, 0.007677600002352847], [0.021612000004097354, 0.012355200000456534, 0.06205600001703715, 0.03160800000841846, 0.08644800001638941, 0.04322400000819471, 0.08213919998888741, 0.1448544000304537, 0.03602000000682892, 0.020191200001136167, 0.18621600004917127, 0.014408000002731569, 0.0072040000013657846, 0.10251840002820245, 0.006177600000228267, 0.02059200000076089, 0.0370656000013696, 0.02471040000091307, 0.021612000004097354, 0.057632000010926276, 0.24392480003007222, 0.04606560001411708], [0.057632000010926276, 0.028828800001065247, 0.1503456000391452, 0.040132800007995684, 0.08644800001638941, 0.04322400000819471, 0.10135839998474694, 0.10450880002463236, 0.061420800018822774, 0.057632000010926276, 0.2035520000536053, 0.014408000002731569, 0.0072040000013657846, 0.1580400000420923, 0.006177600000228267, 0.030888000001141336, 0.03912480000144569, 0.0185328000006848, 0.021612000004097354, 0.08644800001638941, 0.3010960000283376, 0.015355200004705694], [0.03602000000682892, 0.0370656000013696, 0.18964800005051075, 0.03160800000841846, 0.08644800001638941, 0.04322400000819471, 0.10662079998292029, 0.08818880001854268, 0.09213120002823416, 0.08644800001638941, 0.2575040000665467, 0.014408000002731569, 0.0072040000013657846, 0.13667520003582467, 0.006177600000228267, 0.026769600000989158, 0.04942080000182614, 0.014414400000532623, 0.06094720001783571, 0.03602000000682892, 0.31679360002090107, 0.007677600002352847], [0.057632000010926276, 0.03912480000144569, 0.2007744000547973, 0.04036160000759992, 0.03602000000682892, 0.04322400000819471, 0.09701119998499053, 0.1033488000248326, 0.09213120002823416, 0.08644800001638941, 0.19085600004837033, 0.014408000002731569, 0.007677600002352847, 0.0871296000223083, 0.006177600000228267, 0.016473600000608712, 0.0370656000013696, 0.0185328000006848, 0.028816000005463138, 0.021612000004097354, 0.2882080000235874, 0.021612000004097354], [0.028816000005463138, 0.035006400001293514, 0.18195360004756367, 0.08177120002073934, 0.021612000004097354, 0.04322400000819471, 0.08854559998508194, 0.08866240001952974, 0.03602000000682892, 0.08644800001638941, 0.09186560002490296, 0.028816000005463138, 0.038388000011764234, 0.10506720002740622, 0.014414400000532623, 0.02059200000076089, 0.0185328000006848, 0.014414400000532623, 0.021612000004097354, 0.06094720001783571, 0.26313440001104027, 0.007677600002352847], [0.06483600001229206, 0.04118400000152178, 0.2050368000564049, 0.1223616000279435, 0.021612000004097354, 0.04322400000819471, 0.10753599998133723, 0.12237760002972209, 0.061420800018822774, 0.08644800001638941, 0.11772640002891421, 0.021612000004097354, 0.04606560001411708, 0.0871296000223083, 0.02059200000076089, 0.016473600000608712, 0.02059200000076089, 0.02059200000076089, 0.021612000004097354, 0.028816000005463138, 0.31960320000871434, 0.038388000011764234], [0.0, 0.002059200000076089, 0.007465600003342843, 0.007694400002947077, 0.014408000002731569, 0.014408000002731569, 0.009151999998721294, 0.02391360000547138, 0.0, 0.006630399999266956, 0.02391360000547138, 0.0072040000013657846, 0.0, 0.007923200002551312, 0.002059200000076089, 0.002059200000076089, 0.004118400000152178, 0.004118400000152178, 0.007677600002352847, 0.00010000000111176632, 0.027180800003407057, 0.0]])
   #end_time = time.time() - start_time
   #print ("time taken ",end_time)
