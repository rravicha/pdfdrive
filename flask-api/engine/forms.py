from math import sqrt, atan2, ceil, degrees
from datetime import datetime as dt
from copy import deepcopy
from flask.logging import default_handler
import logging


log_f="%(levelname)s %(asctime)s - %(message)s -->%(lineno)d |%(module)s "
logging.basicConfig(
filename="monitor.txt",
level=logging.DEBUG,
format=log_f,
filemode='a+'
)
l=logging.getLogger()
l.addHandler(default_handler)

class Compute:
    def __init__(self,req):
        l.info(f"Request : {req}")
        self.player         =str(req.get('ply'))
        self.dimensions     =[int(i) for i in req.get('dim').split(',')]
        self.pos            =[int(i) for i in req.get ('pp').split(',')]
        self.guard_pos      =[int(i) for i in req.get ('tp').split(',')]
        self.distance       =int(req.get('dist')) 

        self.room_x         = self.dimensions[0]
        self.room_y         = self.dimensions[1]
        self.player_x       = self.pos[0]
        self.player_y       = self.pos[1]
        self.guard_x        = self.guard_pos[0]
        self.guard_y        = self.guard_pos[1]
        self.max_distance   = self.distance

        self.max_x = self.player_x + self.distance + 1
        self.max_y = self.player_y + self.distance + 1
        self.out=None

    def validate(self):

        if not(1<self.room_x<=1250):
            self.out=f"dimension (x {self.room_x}) of the room should be <= than 1250 "
        if not(1<self.room_y<=1250):
            self.out=f"dimension (y {self.room_y}) of the room should be <= than 1250 "
        if ((self.player_x==self.guard_x) and (self.player_y==self.guard_y)):
            self.out=f"player and target shouldn't be sharing same position{self.player_x,self.guard_x,self.player_y,self.guard_y}"
        if (not(0<self.player_x<self.room_x) or not(0<self.player_y<self.room_y)):
            self.out=f"player is positioned self.outside the room {self.player_x,self.player_y} dim {self.room_x,self.room_y}"
        if (not(0<self.guard_x<self.room_x) or not(0<self.guard_y<self.room_y)):
            self.out=f"target is positioned self.outside the room {self.guard_x,self.guard_y} dim {self.room_x,self.room_y}"
        if not(1<self.max_distance<=10000):
            self.out=f"distance is limited to range of  1-10000 but received {self.max_distance}"
        
        if self.out == None:
            return True,self.out
        else:
            l.critical(f"Validation Error : {self.out}")
            return False,self.out

    def get_dist(self, point_x, point_y):
        """Gets distance between player and a point"""
        dist = sqrt((point_x - self.player_x) ** 2 + (point_y -
                                                      self.player_y) ** 2)
        return dist

    def get_angle(self, point_x, point_y):
        """Gets angle between player and a point in RAD"""
        angle = atan2(point_y - self.player_y, point_x - self.player_x)
        # print(f"point_x {point_x} point_y {point_x} angle {angle}")
        return angle

    def get_first_quadrant(self):
        """gets the number of copies that need to be done along the axis
        and gets all the guard and player coords"""
        num_copies_x = ceil(self.max_x / self.room_x)
        num_copies_x = int(num_copies_x)
        num_copies_y = ceil(self.max_y / self.room_y)
        num_copies_y = int(num_copies_y)

        player_exp_x = []
        player_exp_y = []
        guard_exp_x = []
        guard_exp_y = []
        # Loop expands along the x axis
        for i in range(0, num_copies_x + 1, 1):
            temp_player_y_list = []
            temp_guard_y_list = []
            r_x = self.room_x * i

            if len(player_exp_x) == 0:
                n_p_p_x = self.player_x
            else:
                n_p_p_x = (r_x - player_exp_x[-1][0]) + r_x
            player_exp_x.append([n_p_p_x, self.player_y, 1])

            if len(guard_exp_x) == 0:
                n_g_p_x = self.guard_x
            else:
                n_g_p_x = (r_x - guard_exp_x[-1][0]) + r_x
            guard_exp_x.append([n_g_p_x, self.guard_y, 7])

            # Loop expands along the x axis
            for j in range(1, num_copies_y + 1, 1):
                r_y = self.room_y * j
                if len(temp_guard_y_list) == 0:
                    n_g_p_y = (r_y - self.guard_y) + r_y
                    temp_guard_y_list.append(n_g_p_y)
                else:
                    n_g_p_y = (r_y - temp_guard_y_list[-1]) + r_y
                    temp_guard_y_list.append(n_g_p_y)
                guard_exp_y.append([n_g_p_x, n_g_p_y, 7])

                if len(temp_player_y_list) == 0:
                    n_p_p_y = (r_y - self.player_y) + r_y
                    temp_player_y_list.append(n_p_p_y)
                else:
                    n_p_p_y = (r_y - temp_player_y_list[-1]) + r_y
                    temp_player_y_list.append(n_p_p_y)
                player_exp_y.append([n_p_p_x, n_p_p_y, 1])

        return player_exp_x + guard_exp_x + player_exp_y + guard_exp_y

    def other_quadrants(self, matrix):
        """Uses the list from the first quadrant and flips its to the other
        3 quadrants"""
        q2 = deepcopy(matrix)
        q2t = [-1, 1]
        q2f = []
        for j in range(len(q2)):
            list = [q2[j][i] * q2t[i] for i in range(2)]
            dist = self.get_dist(list[0], list[1])

            if dist <= self.max_distance:
                list.append(matrix[j][2])
                q2f.append(list)

        q3 = deepcopy(matrix)
        q3t = [-1, -1]
        q3f = []
        for j in range(len(q3)):
            list = [q3[j][i] * q3t[i] for i in range(2)]
            dist = self.get_dist(list[0], list[1])

            if dist <= self.max_distance:
                list.append(matrix[j][2])
                q3f.append(list)

        q4 = deepcopy(matrix)
        q4t = [1, -1]
        q4f = []
        for j in range(len(q3)):
            list = [q4[j][i] * q4t[i] for i in range(2)]
            dist = self.get_dist(list[0], list[1])

            if dist <= self.max_distance:
                list.append(matrix[j][2])
                q4f.append(list)

        return q2f, q3f, q4f

    def filter_target_hit(self, matrix):
        """Uses a dict with angles as key
        Filters by range and by distance of the same angle (closer always
        wins)"""
        target = {}
        for i in range(len(matrix)):
            dist = self.get_dist(matrix[i][0], matrix[i][1])
            angle = self.get_angle(matrix[i][0], matrix[i][1])
            test_a = self.max_distance >= dist > 0
            test_b = angle not in target
            test_c = angle in target and dist < target[angle][1]
            if test_a and (test_b or test_c):
                target[(angle)] = [matrix[i], dist]
        return target

    @staticmethod
    def return_count(dict):
        count = 0
        for key in dict:
            if dict[key][0][2] == 7:
                count += 1
        return count

    def calculate(self):
        st=dt.utcnow()
        try:
            q1 = self.get_first_quadrant()       
            q2, q3, q4 = self.other_quadrants(q1)
            final_list = q1 + q2 + q3 + q4
            final_dict = self.filter_target_hit(final_list)

            rads=[]
            final_angles=[]

            for key,val in final_dict.items():
            	if int(val[0][2])==7:
            		if (float(key)) <0:
            			rads.append(float(key))
            		else:
            			rads.append(float(key))

            deg=[degrees(r) for r in rads]
            for d in deg:
            	if d<0:
            		final_angles.append(abs(d)+float(180))
            	else:
            		final_angles.append(d)
        except Exception as e:
            l.critical(str(e))
            return str(e)
            
        et=dt.utcnow()
        tt=str(et-st) 

        resp        = {
                'player':self.player,
                'no_of_direction':len(final_angles),
                'angles':final_angles,
                'time taken':tt
                 }
        
        l.info(f"Response : {resp}")
        return resp 

"""
         Makes a room instance with all the parameters given
         Generates all possible points in the first quadrant
         Get all position in all  other quadrants
         Filters the Original player, and all unattainable guards
"""