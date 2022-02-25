
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel

#
# Add your Robot Simulator here
#
class RobotSim:
    
    # init
    def __init__(self, sm, tm, om):
        print("Hello World")
        self.__sm = sm
        self.__tm = tm
        self.__om = om
        
        #x, y, h = self.__sm.get_grid_dimensions()
        #self.__state = state
        #self.__sm.pose_to_state(random.randint(0, x), 
        #                                       random.randint(0, y), 
        #                                       random.randint(0, h))
        
        
    # new move
    def move(self, state):
        x, y, h = self.__sm.state_to_pose(state)
        if at_wall(x, y, h) or random.random() < 0.3
            print("At wall in move. Geting new heading")
            h = new_heading(x, y, h)
        state = self.__sm.pose_to_state(new_move(x, y, h))
        return state
    
    def at_wall(self, x, y, h):
        width, height, heading = self.__sm.get_grid_dimensions()
        
        if h == 0 and y == height - 1:
            return True
        elif h == 1 and x == width -1:
            return True
        elif h == 2 and y == 0:
            return True
        elif h == 3 and x == 0:
            return True
        return False
    
    def new_heading(x, y, h):
        headings = [0,1,2,3]
        random.shuffle(headings)
        for new in headings:
            if !at_wall(x, y, new):
                return new
    
    def new_move(x, y, h):
        if h == 0:
            return x, y + 1, h
        elif h == 1:
            return x + 1, y, h
        elif h == 2:
            return x, y - 1, h
        elif h == 3:
            return x - 1, y, h
        print("Något gick fel i new_move i robotsim")
        return x, y, h
    
    # get sensor reading
    def get_sensor_reading(self, state):
        n_read = self.__om.get_nr_of_readings()
        probabilities = np.zeros(n_read)
        
        for n in range(n_read):
            probabilities[i] = self.__om.get_o_reading_state(self.__sm.state_to_pose(n))
            
        choices = list(range(len(probabilities) - 1))
        return random.choices(choices, probabilities)
#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#
class HMMFilter:
    def __init__(self, tm, om):
        print("Hello (again) World")
        self.__tm = tm
        self.__om = om
        
    
    def forward_filter(self, probabilities, sensor_reading):
        o = self.__om.get_o_reading(sensor_reading)
        t = self.__tm.get_T_transp()
        
        p = 0 @ t @ probabilities
        
        return (1/np.linalg.norm(probs))*p
        
