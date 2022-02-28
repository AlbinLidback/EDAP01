
from operator import pos
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel

#
# Add your Robot Simulator here
#

class RobotSim:
    def __init__(self, sm : StateModel, true_state):
        self.sm : StateModel = sm 
        self.true_state = true_state           

        self.rows, self.cols, self.head = self.sm.get_grid_dimensions()

        print("Hello World / RobotSim")

    def possibleHeadings(self, x, y):
            possible_heading = []
            if x > 0:
                possible_heading.append(0)
            if x < self.rows-1:
                possible_heading.append(2)
            if y > 0:
                possible_heading.append(3)
            if y < self.cols-1:
                possible_heading.append(1)

            return possible_heading

    def next_state(self) -> int :
        x,y,h = self.sm.state_to_pose(self.true_state)          # current pose
        possible_headings = self.possibleHeadings(x,y)

        if h in possible_headings:              #No wall in front of robot
            prob = random.random()
            if prob < 0.3:
                prev = h
                while prev == h:
                    h = random.choice(possible_headings)
        else:
            h = random.choice(possible_headings)

        #get new position
        x -= h == 0
        y += h == 1
        x += h == 2
        y -= h == 3
        self.true_state = self.sm.pose_to_state(x,y,h)

        return self.true_state

    def robot_sensing(self,x, y):               
        #Coordinates for ls and ls2
        ls = [(x+a, y+b) for a,b in [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0, -1), (1, -1)]]
        ls2 = [(x+a, y+b) for a,b in [(2,-2), (2,-1), (2,0), (2,1), (2,2), (-2,-2), (-2,-1), (-2,0), (-2,1), (-2,2), (1,2), (0,2), (-1,2), (1,-2), (0,-2), (-1,-2)]]
        
        #remove all coordinates outside grid
        inside_grid = lambda xy: xy[0] >= 0 and xy[0] < self.rows and xy[1] >= 0 and xy[1] < self.cols 
        ls = list(filter(inside_grid, ls))
        ls2 = list(filter(inside_grid, ls2))

        prob = random.random()

        #probability thresholds
        trueLocation_prob = 0.1
        ls_prob = trueLocation_prob + len(ls) * 0.05
        ls2_prob = ls_prob + len(ls2) * 0.025

        #return based on prob
        if prob <= trueLocation_prob:
            return self.sm.state_to_position(self.true_state)
        elif prob <= ls_prob:
            return random.choice(ls)
        elif prob <= ls2_prob:
            return random.choice(ls2)
        else:
            return None

#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#

class HMMFilter:
    def __init__(self, sm, tm, ob):
        self.sm : StateModel = sm
        self.tm : TransitionModel = tm
        self.ob : ObservationModel = ob
        print("Hello again, World / HMMFilter")
    
    def filtering(self, sense, probs):
        #Get sensed position as reading
        senseReading = self.sm.position_to_reading(sense[0], sense[1]) if sense else None

        T_trans = self.tm.get_T_transp()
        O = self.ob.get_o_reading(senseReading)
        probs = np.matmul(np.matmul(O, T_trans), probs)       
        
        probs = (1.0 / sum(probs) ) * probs         #Normalize
        
        #print most likely states for debugging
        # topStates = (-probs).argsort()[:5]
        # for s in topStates:
        #     print("Pose:", self.sm.state_to_pose(s), "Likelihood:", res[s])

        #estimate = self.sm.state_to_position(np.argmax(res))

        #sum probabilitites of states corresponding to the same position 
        estimate = self.getEstimate(probs)
        return probs, estimate
    
    def getEstimate(self, probs):
        probabilities = {}
        for i, p in enumerate(probs):
            pos = self.sm.state_to_position(i)
            probabilities[pos] = probabilities.get(pos, 0) + p
        
        return max(probabilities, key=probabilities.get)



        
        
        