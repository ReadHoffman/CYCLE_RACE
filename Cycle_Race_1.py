# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 21:20:00 2019

@author: Read
"""

#import random
import pygame
import math
import numpy as np
#from numpy.linalg import matrix_rank
import random
import pandas as pd
import time


#maybe make this an input with max limit
racers_n = 12 

#hardcode dimensions of bike, lots of things will be based off of this
# like roadwidth, distance between bikes etc
bike_wid = 8
bike_len = bike_wid*3
 
# Define some colors to be used for teams
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
TEAL = (51, 204, 204)
YELLOW = (255, 255, 0)

team_colors_list = [WHITE,GREEN,RED,BLUE,TEAL,YELLOW]

# Set the width xaxis and height y axis of the screen
size = [1400, 700]


#road will be straight across middle of window
#find midpoint of screen to create starting locations and paths 
road_midpoint_y = size[1]/3 #2/3 up screen, middle of the road
start_line_x = size[0]*.1 #10% of way across screen
finish_line_x = size[0]*.95 #95% of way across screen
max_bikes_across_road = 12
road_width = bike_wid*(max_bikes_across_road*1.2) # road should allow this many bikes with a buffer
road_upper_y = road_midpoint_y-(road_width/2)
road_lower_y = road_midpoint_y+(road_width/2)
max_bikes_wide = bike_wid*max_bikes_across_road #max amount of space taken by 8 bikes across road
bike_buffer_y = (road_width-max_bikes_wide)/max_bikes_across_road
bike_buffer_x = bike_len*.3 # bikes ride within 30% of bike length of other bikes
bike_columns = math.ceil(racers_n/max_bikes_across_road)
first_racer_start_x = start_line_x*.95
first_racer_start_y = road_upper_y-bike_buffer_y-(bike_wid/2)
bike_len_in_km = 0.00185 #185cm per UCI max len
course_len_in_km = 50
course_len_in_px = finish_line_x-start_line_x
course_px_per_km = course_len_in_px/course_len_in_km
course_halfway = course_len_in_px/2 + start_line_x

elevation_range_m = 5000 #consider swapping this in for elevation range
elevation_list = []
for i in range(random.randrange(10,30)):
    x = random.randrange(0,course_len_in_km)
    y = random.randrange(int(-elevation_range_m*.2),int(elevation_range_m*.8))
    elevation_list.append([x,y])
    
elevation_list.append([0,random.randrange(int(-elevation_range_m*.2),int(elevation_range_m*.8))])   
elevation_list.append([course_len_in_km,random.randrange(int(-elevation_range_m*.2),int(elevation_range_m*.8))])   
 
#elevation_list = [[0,0],[2,-50],[5,200],[7,800],[20,-100],[22,600],[25,300],[27,1200],[40,150],[41.5,1500],[44,550],[48,300],[50,250]]
course_elevation = pd.DataFrame(elevation_list,columns=['KM','ELEVATION'])
course_elevation = course_elevation.sort_values(by='KM').reset_index(drop=True)

elevation_range = max(course_elevation['ELEVATION'])-min(course_elevation['ELEVATION'])

course_elevation['KM_DRAW']=course_elevation['KM']/course_len_in_km*course_len_in_px
course_elevation['ELEVATION_DRAW']=road_width/elevation_range_m*course_elevation['ELEVATION'] #pixels per km
course_elevation['X'] = start_line_x+course_elevation['KM_DRAW']
course_elevation['Y'] = road_lower_y+(min(course_elevation['ELEVATION_DRAW']))-course_elevation['ELEVATION_DRAW']
#rects

##finish rect intended to show sprint
##should represtent last 2k of the course zoomed in
buffer_finish_y = .05
buffer_finish_x = .1
finish_rect_h = road_upper_y*(1-buffer_finish_y*2)
finish_rect_w = course_len_in_px*(1-buffer_finish_x*2)
finish_rect_y = road_upper_y*buffer_finish_y
finish_rect_x = start_line_x+course_len_in_px*buffer_finish_x
finish_rect_finish_x = finish_rect_x+(finish_rect_w*.9)

finish_rect = pygame.Rect(finish_rect_x, finish_rect_y, finish_rect_w, finish_rect_h)

##group rect
##will need to be repeated up to 6 times so all references should be relative
group_box_num = 1
group_box_offset_x = 0
group_box_offset_y = 0
group_box_buffer_y = .05
group_box_buffer_x = buffer_finish_x
boxes_space = size[1]-road_lower_y 
num_boxes_y = 3 #goal distribute boxes evenly
group_box_y_buffers = num_boxes_y+1 # num of buffers needed y
# x buffer handled differently since goal is match finish rect width


##gameplay items
#adjust speed to make it appropriate for game
spd_adjust = .10

#find starting location and increment up until bikes don't fit on road, then go to next row
#racer_list = []  # delete if works
racer_df_cols=['i'
               ,'racer_x'
               ,'racer_y'
#del               ,'racer_draft_back_x_y'
               ,'racer_draft_back_x'
               ,'racer_draft_back_y'
               ,'racer_target'
#del               ,'racer_target_x_y'
               ,'racer_target_x'
               ,'racer_target_y'
               ,'racer_actual_spd'
               ,'racer_cruise_spd'
               ,'racer_cruise_chg'
               ,'racer_surge_spd'
               ,'racer_surge_chg'
               ,'racer_attack_spd'
               ,'racer_attack_chg'
               ,'racer_polygon'
               ]
racer_df = pd.DataFrame(columns=racer_df_cols)
for i in range(racers_n): #bike number 9 should be the 1st bike in column 2
    racer_start_col = math.ceil((i+1)/max_bikes_across_road)  #i=8 #col = 1 aka 2ndcolumn
    racer_start_row = i-(racer_start_col*max_bikes_across_road) #i=8- (1*8) = 0 aka 1st row
    modify_start_y = (-bike_buffer_y-bike_wid)*racer_start_row # (-2-8) * 0 = 0
    modify_start_x = (-bike_buffer_x-bike_len)*(racer_start_col-.5) #
    racer_x = first_racer_start_x+modify_start_x
    racer_y = first_racer_start_y+modify_start_y
#del    racer_draft_back_x_y = [racer_x-bike_len-bike_buffer_x,racer_y]
    racer_draft_back_x = racer_x-bike_len-bike_buffer_x
    racer_draft_back_y = racer_y
    racer_target = np.NaN
    racer_target_x = 0.0
    racer_target_y = 0.0
    racer_actual_spd = 0
    racer_cruise_spd = 22*spd_adjust
    racer_cruise_chg = 1*spd_adjust
    racer_surge_spd = 30*spd_adjust
    racer_surge_chg = 2*spd_adjust
    racer_attack_spd = 42*spd_adjust
    racer_attack_chg = 4*spd_adjust
    racer_polygon = []#[[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0]]
#    zip_pos = zip(first_racer_start_xy, [modify_start_x,modify_start_y]) #can delete if works
#    start_pos_racer = [a + b for a, b in zip_pos] #can delete if works
#    start_pos_indexed = [i,start_pos_racer ] #can delete if works
    racer_info = [i
                  ,racer_x
                  ,racer_y
#del                  ,racer_draft_back_x_y
                  ,racer_draft_back_x
                  ,racer_draft_back_y
                  ,racer_target
#del                  ,racer_target_x_y
                  ,racer_target_x
                  ,racer_target_y
                  ,racer_actual_spd
                  ,racer_cruise_spd
                  ,racer_cruise_chg
                  ,racer_surge_spd
                  ,racer_surge_chg
                  ,racer_attack_spd
                  ,racer_attack_chg
                  ,racer_polygon
                  ]
    racer_df.loc[len(racer_df)] = racer_info 
racer_df.racer_polygon = racer_df.racer_polygon.astype(object)   
 

def UPDATE_POLYGON():    
    for i in range(len(racer_df)):
        polygon_nnw = [float(racer_df.loc[i,'racer_x'])-(bike_len/6),float(racer_df.loc[i,'racer_y'])-(bike_wid/2)]
        polygon_nne = [float(racer_df.loc[i,'racer_x'])+(bike_len/6),float(racer_df.loc[i,'racer_y'])-(bike_wid/2)]
        polygon_e = [float(racer_df.loc[i,'racer_x'])+(bike_len/2),float(racer_df.loc[i,'racer_y'])]
        polygon_sse = [float(racer_df.loc[i,'racer_x'])+(bike_len/6),float(racer_df.loc[i,'racer_y'])+(bike_wid/2)]
        polygon_ssw = [float(racer_df.loc[i,'racer_x'])-(bike_len/6),float(racer_df.loc[i,'racer_y'])+(bike_wid/2)]
        polygon_w = [float(racer_df.loc[i,'racer_x'])-(bike_len/2),float(racer_df.loc[i,'racer_y'])]
        point_list = [polygon_nnw,polygon_nne,polygon_e,polygon_sse,polygon_ssw,polygon_w]
        racer_df.at[i,'racer_polygon'] = point_list #broken
UPDATE_POLYGON()


#limit to fields index, x, and y data for each racer and convert to numpy array
current_x_y = np.asarray(racer_df[['i','racer_x','racer_y']])

#create array the right size based on number of racers
#this array will be used to manager the relationships between riders
relations_array_len = (racers_n**2)-racers_n

#columns=['Racer_1', 'Racer_1x', 'Racer_1y','Racer_2', 'Racer_2x', 'Racer_2y','Distance']
current_relations = np.zeros([relations_array_len,7])
def compute_relations():
    cr_i=0
    # cartesian join where rider is not equal to themselves to create relationships
    for x in range(len(current_x_y)):
        for y in range(len(current_x_y)):
            if x != y:
                current_relations[cr_i,0:6] =  list(current_x_y[x,:])+list(current_x_y[y,:])
                cr_i = cr_i+1           
            else:
                continue
    
    #calculate distance between 2 points, will be for drafting, pathing and decision making
    for i in range(len(current_relations)):
        dist_x_diff = current_relations[i][1]-current_relations[i][4]
        dist_y_diff = current_relations[i][2]-current_relations[i][5]
        hypot = math.hypot(dist_x_diff, dist_y_diff)        
        current_relations[i,6] = hypot
   

compute_relations()
#sort by so we can select closest rider or riders iteratively
current_relations = current_relations[current_relations[:,6].argsort(kind='mergesort')]
current_relations = current_relations[current_relations[:,0].argsort(kind='mergesort')]


#fix this as it isn't a group rank
racer_df['live_rank'] = racer_df['racer_x'].rank(method='first')  #ties broken
last_back = int(racer_df[  max(racer_df['live_rank']) == racer_df['live_rank'] ]['i'])
first_rider = int(racer_df[  min(racer_df['live_rank']) == racer_df['live_rank'] ]['i'])


#last_back_relations = current_relations[current_relations[:,0]==last_back]
#for i in range(len(last_back_relations)):
#    nearest_qualified_racer = last_back_relations[i,3]
#    me = last_back_relations[i,0]
#    speed_nearest = racer_df.loc[nearest_qualified_racer,'racer_actual_spd']
#    speed_me = racer_df.loc[me,'racer_actual_spd']
#    dist_nearest = last_back_relations[i,6] 
#    req_dist = bike_len*2
#    if speed_nearest>speed_me and dist_nearest<req_dist:
#        racer_df.loc[me,'racer_target'] = nearest_qualified_racer
#        racer_target_x_y[me,'racer_target_x_y'] = racer_df[nearest_qualified_racer,[racer_x,racer_y]]
#    
#        break
#    else:
#        continue

gap_definition = bike_len*3  

##default rules
#1 if there is a racer around you without a draft going faster than you, follow them, if not ride at cruise
#2 if you are the front of a group, wait 10 seconds and drop back
#3 forward riders get to pick a target first
    
#picking a target



def select_target(racer=0,distance=bike_len*3):
    #select available targets for individual racer
    available_targets = current_relations[current_relations[:,0]==racer]
    #limit those targets by distance
    nearby_targets = available_targets[available_targets[:,6]<=distance,3]
    #get info on those nearby targets
    nearby_target_details = racer_df.loc[racer_df.i.isin(nearby_targets)]
    #get the current speed of the individual racer 
    racer_act_spd = int(racer_df.loc[racer_df.loc[:,'i']==racer,'racer_actual_spd'])
    #set threshold for filtering targets, i don't want a racer going after someone who is only going .05% faster
    speed_variance_threshold = 1.03 #x percent faster
    #limit nearby targets to those exceeding the speed threshold
    nearby_targets =nearby_target_details[nearby_target_details['racer_actual_spd']>=racer_act_spd*speed_variance_threshold]
    #sort remaining targets by speed descending
    nearby_targets=nearby_targets.sort_values(by='racer_actual_spd', ascending=False).reset_index(drop=True)
    #pick the fastest target and set it as the racer target for the individual racer
    racer_df.at[racer_df.loc[:,'i']==racer,'racer_target'] = nearby_targets.loc[0,'i']
    #find the draft back point of that target racer and set it as the target x y for the individual racer
    racer_df.loc[racer_df.i==racer,'racer_target_x'] = nearby_targets.at[0,'racer_draft_back_x']
    racer_df.loc[racer_df.i==racer,'racer_target_y'] = nearby_targets.at[0,'racer_draft_back_y']
    
select_target()

###line intersection checker, borrowed this code from stackoverflow
def line_intersection(curr_x=0, curr_y=0,next_x=5,next_y=5,pg_fr_x=2,pg_fr_y=0,pg_to_x=0,pg_to_y=2):
    is_intersection = True
    line1 = [[curr_x,curr_y],[next_x,next_y]]
    line2 = [[pg_fr_x,pg_fr_y],[pg_to_x,pg_to_y]]
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = float(det(xdiff, ydiff))
    if div == 0.0:
       is_intersection = False

#    d = (det(*line1), det(*line2))
#    x = det(d, xdiff) / div
#    y = det(d, ydiff) / div
    return is_intersection

line_intersection() #test

###check all points of riders to see if movement will intersect
def check_for_obstruction(racer=0,curr_x=0,curr_y=0,next_x=0,next_y=0):
    result = False
    racer_grp = int(racer_df.loc[racer_df.i==racer,'racer_group']) #limited to only riders in that group
    mask = (racer_df.i!=racer) & (racer_df.racer_group==racer_grp)
    oth_racer_rect_list = racer_df.loc[mask,'racer_polygon'] 
    racer_pt_list = racer_df.loc[racer_df.i==racer,'racer_polygon'][0]
    racer_x_diff = next_x-curr_x
    racer_y_diff = next_y-curr_y
    
    for pt in range(len(racer_pt_list)):
        racer_curpt_x = racer_pt_list[pt][0]
        racer_curpt_y = racer_pt_list[pt][1]
        racer_nxtpt_x = racer_curpt_x+racer_x_diff
        racer_nxtpt_y = racer_curpt_y+racer_y_diff

    
        for rect in oth_racer_rect_list: #loop through racer polygon point lists
            for i in range(len(rect)+1): #create a counter to loop through the points in the rect
                if i==len(rect): i=0
                if i==len(rect)-1: nxt = 0
                else: nxt=i+1
                pg_from_x = rect[i][0]
                pg_from_y = rect[i][1]
                pg_toward_x = rect[nxt][0]
                pg_toward_y = rect[nxt][1]      
                
                #check for line segment intersection
                if line_intersection(racer_curpt_x, racer_curpt_y,racer_nxtpt_x,racer_nxtpt_y,pg_from_x,pg_from_y,pg_toward_x,pg_toward_y) == True:
                    result = True
                else:
                    continue
    return result

check_for_obstruction()



def move_toward_target(raceri=0):
    curr_x = racer_df.loc[racer_df.i==raceri,'racer_x']
    curr_y = racer_df.loc[racer_df.i==raceri,'racer_y']
    targ_x = racer_df.loc[racer_df.i==raceri,'racer_target_x']
    targ_y = racer_df.loc[racer_df.i==raceri,'racer_target_y']
    targ_diff_x = targ_x-curr_x
    targ_diff_y = targ_y-curr_y
    targ_radians = math.atan2(targ_y-curr_y, targ_x-curr_x)
    targ_degrees = math.degrees(targ_radians) #angle
    racer_act_spd = int(racer_df.loc[racer_df.loc[:,'i']==raceri,'racer_actual_spd'])
    racer_cruise_chg = int(racer_df.loc[racer_df.loc[:,'i']==raceri,'racer_cruise_chg']) #hypotenuse
    new_speed = racer_act_spd+racer_cruise_chg
    #todo compute new point based on x y change'
    new_attempted_y = math.cos(targ_degrees)*new_speed
    new_attempted_x = new_attempted_y*math.tan(targ_degrees)
    
    #if that point causes an error, try incrementing in only the y direction (check for intersections)
    if check_for_obstruction(raceri,curr_x,curr_y,new_attempted_x,new_attempted_y) == False:
        print("no obs")
    else:
        print("obs, try incrementing differently")
    #if that point causes an error, then try incrementing only in the x direction (check for intersections)
    
    #if no errors update the x and y coordinates
    
    #update speed
    
start = time.time()
move_toward_target()
end = time.time()
print(end - start)

#identify situation
##for each rider
##look around at riders in my group (25 bike lengths)
##this is complicated, might need function to compute density
#chk_grp_only = bike_len*25
#grp_riders = current_relations[current_relations[:,6]<chk_grp_only]


#for worst rank pick a target rider to follow
## set second to last back rider as my target
##pick point behind that second to last back rider00

#move last back rider toward target point
##increment at some steady rate toward that point

#for best rank rider
## set second to front rider as my target
##pick point in front of that second to front rider

#move front rider toward target point
##increment at some steady rate toward that point





# evaluate group based on gaps between riders
        #try df.groupby('group')['value'].rank(ascending=False)
#racer_df['Data_lagged'] = (racer_df.sort_values(by=['live_rank'], ascending=True)['racer_x'].shift(1))
#racer_df['gap_to_rider_ahead'] = racer_df['racer_x']-racer_df['Data_lagged']

#racer_df['gap_flag'] = [int(x) for x in list(racer_df['gap_to_rider_ahead']>=gap_definition)]
#racer_df['racer_group'] = racer_df.sort_values(by=['live_rank'], ascending=True)['gap_flag'].cumsum()
#racer_group_df = racer_df.groupby('racer_group').count()[['i']]

#def set_target():
#    #is there at least one rider in the polygon in front of me?  if so great!
#    #am i following someone and there is another rider nearby who is going faster?  if so, that rider is my target
#    
#def move_toward_target():
#    x
#    #increment speed by accelleration amt corresponging

#define function that will draw riders in their current xy pos
def racer_x_y_draw_cur_xy(an_array):
    for i in range(len(an_array)):
        polygon_nnw = [float(an_array[i,1])-(bike_len/6),float(an_array[i,2])-(bike_wid/2)]
        polygon_nne = [float(an_array[i,1])+(bike_len/6),float(an_array[i,2])-(bike_wid/2)]
        polygon_e = [float(an_array[i,1])+(bike_len/2),float(an_array[i,2])]
        polygon_sse = [float(an_array[i,1])+(bike_len/6),float(an_array[i,2])+(bike_wid/2)]
        polygon_ssw = [float(an_array[i,1])-(bike_len/6),float(an_array[i,2])+(bike_wid/2)]
        polygon_w = [float(an_array[i,1])-(bike_len/2),float(an_array[i,2])]
        point_list = [polygon_nnw,polygon_nne,polygon_e,polygon_sse,polygon_ssw,polygon_w]
        pygame.draw.polygon(screen,WHITE,point_list,0)


#draw racer shapes on screen at current x/y coordinates
#for testing, can be commented out when it works #it works!
#racer_x_y_draw_cur_xy(current_x_y)

# start pygame
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Bike Race")
clock = pygame.time.Clock() # Used to manage how fast the screen updates

# Loop until the user clicks the close button.
done = False

# -------- Main Program Loop -----------
while not done:
    # --- Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    
    #distance
    dist_remain = course_len_in_km
    
    # --- Bike positions relative to eachother
    compute_relations()
    
    #sort by so we can select closest rider or riders iteratively
    current_relations = current_relations[current_relations[:,6].argsort(kind='mergesort')]
    current_relations = current_relations[current_relations[:,0].argsort(kind='mergesort')]
    
    racer_df.loc[:,'live_rank'] = racer_df.loc[:,'racer_x'].rank(method='first')  #ties broken
    last_back = int(racer_df.loc[  max(racer_df.loc[:,'live_rank']) == racer_df['live_rank'],'i'])
    first_rider = int(racer_df.loc[min(racer_df.loc[:,'live_rank']) == racer_df['live_rank'],'i'])

    racer_df.loc[:,'Data_lagged'] = (racer_df.sort_values(by=['live_rank'], ascending=True)['racer_x'].shift(1))
    racer_df.loc[:,'gap_to_rider_ahead'] = racer_df.loc[:,'racer_x']-racer_df.loc[:,'Data_lagged']
    racer_df.loc[:,'gap_flag'] = [int(x) for x in list(racer_df.loc[:,'gap_to_rider_ahead']>=gap_definition)]
    racer_df.loc[:,'racer_group'] = racer_df.sort_values(by=['live_rank'], ascending=True)['gap_flag'].cumsum()
    racer_group_df = racer_df.groupby('racer_group').count()[['i']]


    
#    last_back_relations = current_relations[current_relations[:,0]==last_back]
#    for i in range(len(last_back_relations)):
#        nearest_qualified_racer = last_back_relations[i,3]
#        me = last_back_relations[i,0]
#        speed_nearest = racer_df.loc[nearest_qualified_racer,'racer_actual_spd']
#        speed_me = racer_df.loc[me,'racer_actual_spd']
#        dist_nearest = last_back_relations[i,6] 
#        req_dist = bike_len*2
#        if speed_nearest>speed_me and dist_nearest<req_dist:
#            racer_df.loc[me,'racer_target'] = nearest_qualified_racer
#            racer_df.loc[me,'racer_target_x_y'] = racer_df[nearest_qualified_racer,['racer_x','racer_y']]
#        
#            break
#        else:
#            continue
    #this didn't NOT work, i think i need to update the racer_df actual speed
    
    
    # --- decision making
    
    # --- speed result
    #depending on position relative to bike in front, draft speed bonus
    #need polygon to detect draft zone
    
    # --- Logic
    # incremement through change in location
    racer_df.loc[:,'racer_actual_spd'] = 0
    
    for i in range(len(racer_df)):  ### this is broken
        speed_mod_rand = 1+random.randint(-3,3)/100  ### this is broken
        racer_df.loc[i,'racer_actual_spd'] = 4*speed_mod_rand  ### this is broken
    
#    if max(current_x_y[:,1])>course_halfway and dist_remain>2:
#        racer_df['racer_actual_spd'] = 1
#    else:
#        racer_df['racer_actual_spd'] = 4
    
    speed_y = 0
    next_x_y = []
    for i in range(len(current_x_y)):
        current_x = float(current_x_y[i,1])
        current_y = float(current_x_y[i,2])
        next_x = current_x+racer_df.loc[i,'racer_actual_spd']        
        next_y = current_y+speed_y
        next_x_y.append([i,next_x,next_y])
    
    current_x_y = np.asarray(next_x_y)
    # --- Drawing
    # Set the screen background
    screen.fill(BLACK)

    #draw course  ##fyi drawing from top left coordinate, not bottom left
    pygame.draw.line(screen,WHITE,(0,road_upper_y),(size[0],road_upper_y),1) #add one pixel to y
    pygame.draw.line(screen,WHITE,(0,road_lower_y-1),(size[0],road_lower_y-1),1)
    pygame.draw.line(screen,WHITE,(start_line_x,road_lower_y-1),(start_line_x,road_upper_y),1) #start line
    pygame.draw.line(screen,WHITE,(finish_line_x,road_lower_y-1),(finish_line_x,road_upper_y),1) #finish line
    
    #draw finishing strait
    pygame.draw.rect(screen, WHITE, finish_rect,1)
    pygame.draw.line(screen,WHITE,(finish_rect_finish_x,finish_rect_y),(finish_rect_finish_x,finish_rect_y+finish_rect_h),1)
    
    #draw group boxes
    n_groups = max(racer_df.loc[:,'racer_group'])
    for i in range(n_groups+1):
        if i % 2 == 0: #if i is even do this
            group_box_offset_x= 0
            group_box_offset_y= math.floor(i/2)
        else: #if i is odd do this
            group_box_offset_x= 1
            group_box_offset_y= math.floor(i/2)

        group_box_h = (boxes_space-group_box_y_buffers)/num_boxes_y
        group_box_w = course_len_in_px/2-(group_box_buffer_x/2)
        group_box_offset_y_amt = group_box_offset_y*(group_box_h+group_box_buffer_y)
        group_box_offset_x_amt = group_box_offset_x*(group_box_w+group_box_buffer_x)
        group_box_y = road_lower_y+((boxes_space/num_boxes_y)*group_box_buffer_y)+group_box_offset_y_amt
        group_box_x = start_line_x+group_box_offset_x_amt
        group_box_rect = pygame.Rect(group_box_x, group_box_y, group_box_w, group_box_h)
        pygame.draw.rect(screen, WHITE, group_box_rect,1)
    
    
    for i in range(len(course_elevation)-1):
        x1 = course_elevation.loc[i,'X']
        y1 = course_elevation.loc[i,'Y']
        x2 = course_elevation.loc[i+1,'X']
        y2 = course_elevation.loc[i+1,'Y']
        pygame.draw.line(screen,WHITE,(x1,y1),(x2,y2),1)
    
    
    # Draw the rectangle
    racer_x_y_draw_cur_xy(current_x_y)
    
 
    # Update database with (now updated) current x y
    for i in range(len(current_x_y)):
        racer_df.loc[i,['i','racer_x','racer_y']] = current_x_y[i,:]
 

    
    
    
    #reduce distance remaining based on lead rider's progress
    dist_remain = dist_remain-.05 #tested this idea as a means to slow them down mid frame, if group boxes work, no need
    
    
    # --- Wrap-up
    # Limit to 60 frames per second
    clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    

 
# Close everything down
pygame.quit()


