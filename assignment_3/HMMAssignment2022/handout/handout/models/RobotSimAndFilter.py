
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel

#
# Add your Robot Simulator here
#
class RobotSim:
    
    # init
    def __init__(self, sm, tm, om, state):
        print("Hello World")
        self.sm = sm
        self.tm = tm
        self.om = om
        
        #x, y, h = self.__sm.get_grid_dimensions()
        
        self.state = state
        self.rows, self.cols, self.head = self.sm.get_grid_dimensions()
        
        #self.__sm.pose_to_state(random.randint(0, x), 
        #                                       random.randint(0, y), 
        #                                       random.randint(0, h))
        
        
    # new move
    def new_move(self) -> int:
        x, y, h = self.sm.state_to_pose(self.state)
        av_headings = self.av_headings(x, y)

        ran = random.random()
        new_h = random.choice(av_headings)
        if h in av_headings and ran >= 0.7:
            new_h = h

        if h == 0:
            x -= 1
        elif h == 1:
            y += 1
        elif h == 2:
            x += 1
        elif h == 3:
            y -= 1

        self.state = self.sm.pose_to_state(x, y, new_h)
        return self.state

    def av_headings(self, x, y):
        av_headings = []

        if x > 0:
            av_headings.append(0)
        if y > 0:
            av_headings.append(3)
        if x < self.rows - 1:
            av_headings.append(2)
        if y < self.cols - 1:
            av_headings.append(1)
        
        return av_headings
   
    # get sensor reading
    def read_sensor(self, x, y):

        layer_1 = []
        for r in range(-1, 1):
            for c in range(-1, 1):
                if r != 0 and c != 0:
                    layer_1.append((x + r, y + c))
        
        layer_2 = []
        for r in range(-2, 2):
            for c in range(-2, 2):
                if abs(r) + abs(c) > 1:
                    layer_2.append((x + r, y + c))

        # TODO ta bort grejer utanför planen
        outside = lambda xy: xy[0] >= 0 and xy[0] < self.rows and xy[1] >= 0 and xy[1] < self.cols 
        layer_1 = list(filter(outside, layer_1))
        layer_2 = list(filter(outside, layer_2))

        prob = random.random()
        true_prob = 0.1
        layer_1_prob = len(layer_1) * 0.05
        layer_2_prob = len(layer_2) * 0.025

        if prob <= true_prob:
            return self.sm.state_to_position(self.state)
        elif prob <= true_prob + layer_1_prob:
            return random.choice(layer_1)
        elif prob <= true_prob + layer_1_prob + layer_2_prob:
            return random.choice(layer_2)
        else:
            return None
    
#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#
class HMMFilter:
    
    def __init__(self, sm, tm, om, state):
        self.sm = sm
        self.tm = tm
        self.om = om
        self.state = state
    
    def forward_filter(self, sens, probs):
        sensReading = None
        if sens:
            sensReading = self.sm.position_to_reading(sens[0], sens[1])

        t_t = self.tm.get_T_transp()
        o = self.om.get_o_reading(sensReading)
        f = o @ t_t @ probs
        
        #f = np.norm(f)
        f = (1.0 / sum(f) ) * f
        print("Max:", max(f))
        return f