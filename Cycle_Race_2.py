# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 15:30:34 2019

@author: Read
"""

import pygame
import math
import random
import time

#set screen dimensions
screen_size = [800,600]

# number of racers
r_qty = 30

# Define some colors to be used for teams
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
TEAL = (51, 204, 204)
YELLOW = (255, 255, 0)

team_qty = 6
team_colors_list = [WHITE,GREEN,RED,BLUE,TEAL,YELLOW]

def speed_test(x):
    start = time.time()
    x
    end = time.time()
    print(end - start) 

def random_coordinate():
    rand_x = random.randint(0,screen_size[0]*100)/100
    rand_y = random.randint(0,screen_size[1]*100)/100
    return [rand_x,rand_y]
#random_coordinate()#test

# main database for rider data
r_df = [[r, # ..0 bib
         random_coordinate(), # ..1 current coordinates
         r % team_qty, # ..2 team
         0.0, # ..3 current speed
         0.01, # ..4 current acc/dec
         team_colors_list[r % team_qty], # ..5 team colors R,G,B
         0, # ..6 live rank all
         0, # ..7 target rider
         [0,0], # ..8 target coordinates
         [0,0], # ..9 waypoint coordinates
         0.0,  # ...10 gap behind
         0.0,  # ...11 gap ahead
         0,  # ...12 group number
         ] for r in range(r_qty)]


#r_df[0][1] = [screen_size[0]*.29,screen_size[1]*.45]
#r_df[1][1] = [screen_size[0]*.38,screen_size[1]*.50]
#r_df[2][1] = [screen_size[0]*.55,screen_size[1]*.55]
############ r_df codes
# ..0 bib
# ..1 current coordinates
# ..2 team
# ..3 current speed
# ..4 current acc/dec
# ..5 team colors R,G,B
# ..6 live rank all
# ..7 target rider
# ..8 target coordinates
# ..9 waypoint coordinates
# .10 gap behind
# .11 gap_ahead
# .12 group number
# .13 


r_height = 4
r_width = 8
dist_for_speedcheck = r_width*5
draftback_buffer = r_width/4
draftside_buffer = r_height/4
r_acc = .01 #del?
r_max_spd = .2
gap_for_group_definition= r_width*10
finish_line_x = 160000 #160 kilometers



def rnd(x):
    return int(x*1000)/1000

#place the racers randomly on the screen
r_default = 0
#def draw_r_on_screen(r=r_default,df=r_df):
#    r_rect = pygame.Rect(  r_df[r][1][0], r_df[r][1][1] , r_width, r_height )
#    pygame.draw.rect(screen, r_df[r][5], r_rect, 1)    

def compute_distance(x1,y1,x2,y2):
    dist_x_diff = x2-x1
    dist_y_diff = y2-y1
    hypot = math.hypot(dist_x_diff, dist_y_diff)        
    return hypot

def is_pt_taken(x=400,y=450,df=r_df):
    result=False
    r_pts_near_x_y = [[df[r][1][0],df[r][1][1]] for r in range(len(df)) if compute_distance(
            x,y,df[r][1][0],df[r][1][1])<r_height*.5 and df[r][0]!=r] #only gather points within 2 bike heights
    if len(r_pts_near_x_y)>0: result=True
    return result
    

def calc_draftback_coordinates(r=0,target=0,df=r_df):
    xt = df[target][1][0]
    yt = df[target][1][1]
    hypot = xt-r_width-draftback_buffer
    draftback_y = rnd(yt)
    draftback_x = rnd(hypot)
    result = [target,[draftback_x,draftback_y]]
    
    xr = df[r][1][0]
    yr = df[r][1][1]

    if is_pt_taken(draftback_x,draftback_y)==True:
        draftside_x = xr-(r_width/2)-draftback_buffer
        if yr > yt:
            draftside_y = rnd(yr+r_height+draftside_buffer)  
        else:
            draftside_y = rnd(yr-r_height-draftside_buffer)
        result = [target,[draftside_x,draftside_y]]
    else: pass
    return result




# cartesian join regenerates relationships
def compute_relations(df=r_df):
    r_df_range = range(len(df))
    #create cartesian product to establish a network of relationships
    rels1 = [  [  df[i][0],df[i][1],df[j][0],df[j][1],0.0,0  ]  for i in r_df_range for j in r_df_range if i != j ]
    rels_range = range(len(rels1))

    #compute hypotenuses and iteratively append them to relations list
    hypot_list = [compute_distance(  rels1[i][1][0],rels1[i][1][1],rels1[i][3][0],rels1[i][3][1]  )  for i in rels_range]
    
    #add speed to relations table, will need the later for sort by fastest
    for i in rels_range:
        rels1[i][4] =  rnd(hypot_list[i])
        rels1_r = rels1[i][0]
        rels1[i][5] = r_df[rels1_r][3] 
    return rels1

####### relations list decoder
# ..0 rider
# ..1 rider xy
# ..2 other rider
# ..3 other rider xy
# ..4 rider calc distance, pythagorean theorum, bitches
# ..5 current speed
    

rels = compute_relations() #this generates a new list given current state of r_df


#sort descending by x coordinate location
def sort_r_df_by_x_loc(df):
    return sorted(r_df, key=lambda e: (e[1][0],e[1][1]), reverse=True)

#sort by index, always do this so as not to mess up indexing
def sort_r_df_by_r_bib(df):
    return sorted(df, key=lambda e: e[0], reverse=False)

len(list(range(3)))
# update live rank data
def update_live_rank(df=r_df):
    r_df_srtd = sort_r_df_by_x_loc(df)
    for i in range(len(r_df_srtd)):
        ### rank
        r_df_srtd[i][6]=i
        
        ### group number
        #compute gap behind current rider, this ended up not being important for groups buut i kept it just incase
        nxt_i = i+1
        if i == len(r_df_srtd)-1: #error handling for last rider
            gap_behind = 0.0
        else:
            gap_behind = r_df_srtd[i][1][0]-r_df_srtd[nxt_i][1][0]
        r_df_srtd[i][10]=rnd(gap_behind)
        
        #compute gap ahead of rider
        pri_i = i-1
        if pri_i == -1: #error handling for first rider
            gap_ahead = 0.0
        else:
            gap_ahead = r_df_srtd[pri_i][1][0]-r_df_srtd[i][1][0]
        r_df_srtd[i][11]=rnd(gap_ahead)
        
        if gap_ahead<gap_for_group_definition:
            grp_nbr = r_df_srtd[i][12]
        else:
            grp_nbr = r_df_srtd[pri_i][12]+1
        r_df_srtd[i][12] = grp_nbr
    
    #resort by bib for cleanliness and allowing indexing on other functions           
    r_df_srtd = sort_r_df_by_r_bib(r_df_srtd) #
    df = r_df_srtd
    return df

# update rank TEST TEST TEST
r_df=update_live_rank(r_df)


# for a specified rider create list of available targets
def id_available_targets(r=0):
    available_targets=[]
    for i in range(len(rels)):
        if rels[i][0]==r and rels[i][1][0]<rels[i][3][0]: #filters to main rider and ensures any target riders are at or ahead of main rider
            available_targets.append(rels[i])
    return available_targets
    
# Delete if above code works   
#    rels_pd = pd.DataFrame(rels)
#    #select available targets for individual racer
#    available_targets = rels_pd.loc[rels_pd.loc[:,0]==r]
#    return available_targets.values.tolist()

# for a specified list, sort that list ascending by distance (x coordinate tiebreak), who cares if x is tied
def sort_filter_rels_by_nearest_fastest(some_rels_list=rels,dist=dist_for_speedcheck):
    # sort asc by distance and tiebreak on x loc
    sort_list = sorted( sorted(some_rels_list, key=lambda e: (e[3][0]),reverse=True ), key=lambda e: (e[4]) )
    sort_filter= [i for i in sort_list if i[4]<=dist]

    sort_filter = sorted(sort_filter, key=lambda e: (e[5]),reverse=True ) #sort desc by speed
    if len(sort_filter)==0:
        return sort_list #if there are no riders nearby, use all riders to select target
    else:
        return sort_filter #if there are riders nearby, use the local riders to select target

## update the target rider number and draft-back coordinates
#def update_target_rider(r_targ=1,r_main=0,df=r_df):
##    df[r_main][7] = r_targ
##    df[r_main][8] = calc_draftback_coordinates(r_targ,df)
#    return [r_targ,calc_draftback_coordinates(r_targ,df)]


# for r_df, update the df with a target value and update target coordinates with that target rider's coordintates
def set_nearest_fastest_target(r=0,df=r_df):
#    rx = df[r][1][0]    #rider x
#    ry = df[r][1][1]    #rider y
#    rtx = df[r][1][0]   #rider current target x
#    rty = df[r][1][1]   #rider current target y
#    if compute_distance(rx,ry,rtx,rty)<r_width/8:
#        pass
#    else:
    avail_targ = id_available_targets(r) #returns rels list of all other riders who are in front of main rider
    if len(avail_targ)==0:
        utr_results=[999,[finish_line_x,screen_size[1]/2]]
    else:
        avail_targ_sorted = sort_filter_rels_by_nearest_fastest(avail_targ) # sort that list by speed
        #don't set new target if in draft zone
        if avail_targ_sorted[0][4]>r_width: 
            updated_target = avail_targ_sorted[0][2]
            utr_results = calc_draftback_coordinates(r,updated_target,df)            
        else: 
            utr_results = [df[r][7],df[r][8]] #distance from target is < 1 bl, don't do anything to df
    
    df[r][7] = utr_results[0]
    df[r][8] = utr_results[1]
    return df


    

###line intersection checker, borrowed this code from stackoverflow
def line_intersection(curr_x=0,curr_y=0,next_x=5,next_y=5,pg_fr_x=0,pg_fr_y=5,pg_to_x=5,pg_to_y=0):
    is_intersection = False
    line1 = [[curr_x,curr_y],[next_x,next_y]]
    line2 = [[pg_fr_x,pg_fr_y],[pg_to_x,pg_to_y]]
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = float(det(xdiff, ydiff))
    if div == 0.0:
       is_intersection = False
    else:
#        d = (det(*line1), det(*line2))
#        x = det(d, xdiff) / div
#        y = det(d, ydiff) / div
        is_intersection = True
    
    return is_intersection

#line_intersection() #test

def generate_pt_list(r=0,df=r_df):
    pt_top_left = df[r][1]
    pt_top_right = [pt_top_left[0]+r_width,pt_top_left[1]]
    pt_bottom_right = [pt_top_right[0],pt_top_right[1]+r_height]
    pt_bottom_left = [pt_bottom_right[0]-r_width,pt_bottom_right[1]]
    
    pt_list = [pt_top_left,pt_top_right,pt_bottom_right,pt_bottom_left]
    return pt_list

###check all points of riders to see if movement will intersect
def check_for_obstruction(curr_x=100,curr_y=100,next_x=400,next_y=400,r=0):
    result = False
    #filter to riders within 5 bike lengths, this should speed up the obstruction evaluation
    dist_for_eval = r_width*500 #TEST
    nearby_racer_list = [i[2] for i in rels if i[0]==r and i[4]<=dist_for_eval]
    if len(nearby_racer_list) != 0:

        racer_pt_list = generate_pt_list(int(r))
        oth_racer_pt_list = []
        for i in range(len(nearby_racer_list)):
            oth_racer_pt_list.append(generate_pt_list(i))
        racer_x_diff = next_x-curr_x
        racer_y_diff = next_y-curr_y
        
        for pt in range(len(racer_pt_list)):
            racer_curpt_x = racer_pt_list[pt][0]
            racer_curpt_y = racer_pt_list[pt][1]
            racer_nxtpt_x = racer_curpt_x+racer_x_diff
            racer_nxtpt_y = racer_curpt_y+racer_y_diff
    
        
            for rect in oth_racer_pt_list: #loop through racer polygon point lists
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
                        result = False
    return result



def id_waypoint(r=0,df=r_df):
    curr_x = df[r][1][0]
    curr_y = df[r][1][1]
    targ_x = df[r][8][0]
    targ_y = df[r][8][1]
    racer_act_spd = df[r][3]
    racer_cruise_chg = df[r][4]
    
    target_r = df[r][7]
    if target_r==999:targ_act_spd=0 #handle error thrown by first place having 999 target
    else: targ_act_spd = df[target_r][3] # filter df for target, return speed

    targ_diff_x = targ_x-curr_x
    targ_diff_y = targ_y-curr_y   
    
    #speed should not exceed the gap length
    distance_to_targ = math.hypot(targ_diff_x,targ_diff_y) 
    
    targ_radians = math.atan2(targ_diff_y, targ_diff_x)
    #targ_degrees = math.degrees(targ_radians) #angle
    
#    #testing how atan works
#    math.atan2(-4,-4)
#    x_test = math.cos(math.atan2(-4,-4))*2
#    y_test = math.sin(math.atan2(-4,-4))*2
#    math.sqrt(x_test**2+y_test**2)
    
    #speed calculations
    new_speed = racer_act_spd
    if racer_act_spd<targ_act_spd*1.05:
        new_speed = min(r_max_spd,racer_act_spd+racer_cruise_chg) #min(distance_to_targ,racer_act_spd+racer_cruise_chg)
    else:
        new_speed = min(r_max_spd,racer_act_spd+(racer_cruise_chg/2)) # min(distance_to_targ,racer_act_spd)
    
    #if rider is within 5 bike lengths of target, slow down
    if distance_to_targ<r_width*5:
        new_speed = max(1,racer_act_spd-racer_cruise_chg) #min(distance_to_targ,racer_act_spd+racer_cruise_chg)
    #update new_speed in r_df
#    df[r][3] = new_speed DEL
        
    #new speed will be the hypotenuse in the new triangle
    new_attempted_x = rnd(curr_x+(math.cos(targ_radians)*new_speed) )
    new_attempted_y = rnd(curr_y+(math.sin(targ_radians)*new_speed ) )
    
#    borders = [[screen_size[0]*.20,screen_size[1]*.20],[screen_size[0]*.80,screen_size[1]*.20],[screen_size[0]*.80,screen_size[1]*.80],[screen_size[0]*.20,screen_size[1]*.80]]
        
    if (new_attempted_y < screen_size[1]*.20 or  new_attempted_y>=screen_size[1]*.80 or new_attempted_x > screen_size[0]*.70 or new_attempted_x<=screen_size[0]*.30):
        new_attempted_y=rnd(screen_size[1]*.50+random.randint(-100,100)) #this has them jumping
        new_attempted_x=rnd(screen_size[0]*.50+random.randint(-50,50))
        
#    #is the waypoint obstructed?
#    is_obstructed = check_for_obstruction(r,curr_x,curr_y,new_attempted_x,new_attempted_y)
#    
#    
#    if is_obstructed == True:
#        waypoint = [curr_x,curr_y]
#    else:
#        waypoint = [new_attempted_x,new_attempted_y]
        
    spd_waypoint = [new_speed,new_attempted_x,new_attempted_y] #TEST
    return spd_waypoint
    
# update df with new current location
def move_toward_target(r=0,df=r_df):
    wp = id_waypoint(r,df)
    df[r][1] = [wp[1],wp[2]]
    df[r][3] = wp[0]
    return df

# start pygame
pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Bike Race")
clock = pygame.time.Clock() # Used to manage how fast the screen updates
font = pygame.font.Font(None, 15)
loop=1

# Loop until the user clicks the close button.
done = False

# -------- Main Program Loop -----------
while not done:
    # --- Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    


    # --- Drawing
    # Set the screen background
    screen.fill(BLACK)
               
    # --- Main game functions

    #all racers need this data
    r_df = update_live_rank(r_df)
    rels = compute_relations(r_df)
    
    
    # i want to iterate start to back so i need to sort asc by rank
    sort_by_rank = sorted(r_df, key=lambda e: (e[6]),reverse=False )
    for i in sort_by_rank:
        r=i[0]

        r_df = update_live_rank(r_df)
        rels = compute_relations(r_df)
        r_df = set_nearest_fastest_target(r,r_df)
        r_df = move_toward_target(r,r_df)        

        r_rect = pygame.Rect(  r_df[r][1][0], r_df[r][1][1] , r_width, r_height ) 
        pygame.draw.rect(screen, r_df[r][5], r_rect, 1) 
        



        
    # --- Wrap-up
    
    #display stuff
    loops_ct = font.render(str(loop), True, pygame.Color('white'))
    screen.blit(loops_ct, (screen_size[0]-50,67))
    loop=loop+1
    fps = font.render(str(int(clock.get_fps())), True, pygame.Color('white'))
    screen.blit(fps, (screen_size[0]-50,50))
    for i in range(len(r_df)):
        df_data = font.render(str(r_df[i]), True, pygame.Color('white'))
        screen.blit(df_data, (20,screen_size[1]-100+20*i))

    # Limit to 60 frames per second
    clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
#    wait = 1000
#    pygame.time.wait(int(wait))
    
 
# Close everything down
pygame.quit()