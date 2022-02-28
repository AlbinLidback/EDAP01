
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
        print("new_move")
        x,y,h = self.sm.state_to_pose(self.state)
        av_headings = self.av_headings(x, y)

        ran = random.random()
        new_h = -1
        if h in av_headings and ran >= 0.7:
            new_h = h
        else: 
            new_h = random.choice(av_headings)

        if h == 0:
            x -= 1
        elif h == 1:
            y += 1
        elif h == 2:
            x += 1
        elif h == 3:
            y -= 1

        self.state = self.sm.pose_to_state(x, y, h)
        return self.state

    def av_headings(self, x, y):
        av_headings = []

        if x > 0:
            av_headings.append(0)
        if y < self.cols-1:
            av_headings.append(1)
        if x < self.rows-1:
            av_headings.append(2)
        if y > 0:
            av_headings.append(3)
        
        return av_headings
   
    # get sensor reading
    def read_sensor(self, x, y) -> int:
        #n_read = self.om.get_nr_of_readings()
        #probabilities = np.zeros(n_read)
        
        #for n in range(n_read):
        #    probabilities[n] = self.om.get_o_reading_state(n, self.state)
            
        #choices = list(range(len(probabilities)))
        
        #return random.choices(choices, probabilities)

# ----------------------------------------------------------------
        Ls = [(x+a, y+b) for a,b in [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0, -1), (1, -1)]]
        Ls2 = [(x+a, y+b) for a,b in [(2,-2), (2,-1), (2,0), (2,1), (2,2), (-2,-2), (-2,-1), (-2,0), (-2,1), (-2,2), (1,2), (0,2), (-1,2), (1,-2), (0,-2), (-1,-2)]]
        
        inside_grid = lambda xy: xy[0] >= 0 and xy[0] < self.rows and xy[1] >= 0 and xy[1] < self.cols 
        Ls = list(filter(inside_grid, Ls))
        Ls2 = list(filter(inside_grid, Ls2))

        # print("x y:", x,y)
        # print("LS:", Ls)
        # print("Ls2:", Ls2)

        prob = random.random()

        trueLocation_prob = 0.1
        ls_prob = len(Ls) * 0.05
        ls2_prob = len(Ls2) * 0.025
        if prob <= trueLocation_prob:
            return self.sm.state_to_position(self.state)
        elif prob <= trueLocation_prob + ls_prob:
            return random.choice(Ls)
        elif prob <= trueLocation_prob + ls_prob + ls2_prob:
            return random.choice(Ls2)
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
        print("forward_filter")

        sens_read = None
        if sens:
            #sens = self.sm.state_to_position(sens)
            print(sens)
            x, y = sens
            sens_read = self.sm.position_to_reading(x, y)

        o = self.om.get_o_reading(sens_read)
        t_t = self.tm.get_T_transp()
        
        f = o @ t_t @ probs

        f = f / np.linalg.norm(f)

        est = self.estimate(f)
        return probs, est
        
    # skriv om    
    def estimate(self, probs):
        probabilities = {}
        for i, p in enumerate(probs):
            pos = self.sm.state_to_position(i)
            probabilities[pos] = probabilities.get(pos, 0) + p
        
        return max(probabilities, key=probabilities.get)