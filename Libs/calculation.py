import math
import numpy as np
import pandas as pd

import logging
logger = logging.getLogger(__name__)

def calculate_distance(start_point, end_point):
    return math.sqrt((start_point[0]-end_point[0])**2 + (start_point[1]-end_point[1])**2)


def calculate_turning_angle(x1, y1, x2, y2, x3, y3):
    """
    Compute the turning angle (in degrees) at point B=(x2, y2) for a path defined by points A=(x1, y1), B=(x2, y2), and C=(x3, y3).
    The turning angle is the angle between vectors AB and BC.
    Positive values represent right turns, negative values represent left turns.
    """

    # Calculate direction vectors
    D1 = (x2 - x1, y2 - y1)  # BA'
    D2 = (x3 - x2, y3 - y2)  # BC

    # Calculate dot product
    dot_product = D1[0]*D2[0] + D1[1]*D2[1]

    # Calculate magnitudes
    mag_D1 = math.sqrt(D1[0]**2 + D1[1]**2)
    mag_D2 = math.sqrt(D2[0]**2 + D2[1]**2)

    # Calculate cosine of the angle
    try:
        cos_theta = dot_product / (mag_D1 * mag_D2)
    except ZeroDivisionError:
        cos_theta = 0
    cos_theta = max(-1, min(1, cos_theta))
    
    # Calculate the angle in radians
    theta_rad = math.acos(cos_theta)

    # Convert the angle to degrees
    theta_deg = math.degrees(theta_rad)

    # Calculate cross product
    cross_product = D1[0]*D2[1] - D1[1]*D2[0]
    
    # If cross product is positive, make the angle negative
    if cross_product > 0:
        theta_deg = -theta_deg

    return theta_deg


def FD_Entropy_Calculator_2D(input_df):
    EPSILON = 1e-10

    def countif(input_list, threshold, less=True):
        count = 0
        for value in input_list:
            if less and value < threshold:
                count += 1
            elif not less and value > threshold:
                count += 1
        return count

    x_list = input_df['X'] # A
    y_list = input_df['Y'] # B

    FRAMES = len(x_list)

    times = [i/50 for i in range(FRAMES)] # C

    delta_x = {} # D
    delta_y = {} # E
    delta_r = {} # F
    thetas = {}  # G

    for i in range(FRAMES):
        if i == 0:
            continue
        temp_x = x_list[i] - x_list[i-1]
        temp_y = y_list[i] - y_list[i-1]
        temp_r = math.sqrt(temp_x**2 + temp_y**2)

        delta_x[i] = temp_x
        delta_y[i] = temp_y
        delta_r[i] = temp_r

        if i>1:
            dot_product = (delta_x[i]*delta_x[i-1] + delta_y[i]*delta_y[i-1])
            product_of_magnitudes = (delta_r[i]*delta_r[i-1])
            value = dot_product / (product_of_magnitudes + EPSILON)
            value = max(-1, min(1, value))
            temp_theta = math.acos(value)*180/math.pi
            thetas[i] = temp_theta

    # r is renamed as thresholds # H
    N1 = {} # I
    # N2 = {} # J
    Cr = {} # K
    sigma = {} # L
    logr = {} # M
    logCr = {} # N
    
    thresholds = [(i+1)/10 for i in range(FRAMES)]
    index_1 = thresholds.index(1)
    thresholds = thresholds[:index_1] + [1.01] + thresholds[(index_1+1):]
    # thresholds[:20] 

    for i in range(FRAMES):
        N1[i] = countif(list(delta_r.values()), thresholds[i])
        Cr[i] = N1[i] / (FRAMES - 1)

        try:
            logCr[i] = math.log10(Cr[i])
        except Exception as e:
            logger.error(f"At i = {i}, Cr[i] = {Cr[i]}")
            logger.error(f"Set Cr[i] to 10e-10")
            Cr[i] = 10e-10
            logCr[i] = math.log10(Cr[i])

        sigma[i] = math.log10(Cr[i]) / math.log10(thresholds[i])
        logr[i] = math.log10(thresholds[i])

    APPROCH = 0.000
    neg_close = -math.inf
    neg_close_pos = -1
    for i, value in enumerate(list(logr.values())):
        if value < APPROCH and value > neg_close:
            neg_close = value
            neg_close_pos = i

    table_index = list(range(-5, 6))
    table_index.reverse()

    FD_df = pd.DataFrame(columns=['number', 'logr', 'logCr', 'x-xbar', 'y-ybar', 
                                  '(x-xbar)(y-ybar)', '(x-xbar)2', '(y-ybar)2', '[yi-(a+bxi)]2'])
    FD_df['number'] = table_index
    LEN = len(table_index)

    for row in range(LEN):
        num = table_index[row]
        num = num + neg_close_pos
        FD_df.iloc[row, 1] = logr[num]
        FD_df.iloc[row, 2] = logCr[num]

    col1 = np.array(FD_df['logr'])
    col2 = np.array(FD_df['logCr'])
    col1_avg = np.average(col1)
    col2_avg = np.average(col2)

    for row in range(LEN):
        FD_df.iloc[row, 3] = FD_df.iloc[row, 1] - col1_avg
        FD_df.iloc[row, 4] = FD_df.iloc[row, 2] - col2_avg
        FD_df.iloc[row, 5] = FD_df.iloc[row, 3] * FD_df.iloc[row, 4]
        FD_df.iloc[row, 6] = FD_df.iloc[row, 3]**2
        FD_df.iloc[row, 7] = FD_df.iloc[row, 4]**2

    variable_b = np.sum(np.array(list(FD_df['(x-xbar)(y-ybar)']))) / np.sum(np.array(list(FD_df['(x-xbar)2'])))
    variable_a = col2_avg - col1_avg * variable_b

    for row in range(LEN):
        FD_df.iloc[row, 8] = (FD_df.iloc[row, 2] - (variable_a + variable_b * FD_df.iloc[row, 1]))**2

    variable_s = np.sqrt(np.sum(FD_df['[yi-(a+bxi)]2']) / (LEN - 2))
    variable_bErr = variable_s / np.sqrt(np.sum(FD_df['(x-xbar)2']))
    variable_aErr = variable_s * np.sqrt((1 / LEN) + col1_avg**2 / np.sum(FD_df['(x-xbar)2']))

    def get_entropy():
        G_array = np.array(list(thetas.values()))
        G_count = (G_array >= 90).sum()
        G_count2 = (G_array < 90).sum()
        G_len = G_array.size

        result = (-1) * G_count/G_len * np.log2(G_count/G_len) - G_count2/G_len * np.log2(G_count2/G_len)

        return result

    #H (Entropy)
    Entropy = get_entropy()

    FractalDimension = variable_b

    # Entropy calculation for 2D movement (optional)
    # Entropy calculation in 2D is context-dependent and might require different approaches

    return FractalDimension, Entropy

# Example usage
# input_df = pd.DataFrame({'X': [1, 2, 3], 'Y': [4, 5, 6]})
# FD, Entropy = FD_Entropy_Calculator_2D(input_df)



def FD_Entropy_Calculator_3D(input_df):

    def countif(input_list, threshold, less=True):
        count = 0
        for value in input_list:
            if less and value < threshold:
                count+=1
            elif not less and value > threshold:
                count+=1
            
        return count

    x_list = input_df['X']
    y_list = input_df['Y']
    z_list = input_df['Z']

    FRAMES = len(x_list)
    
    times = [i/50 for i in range(FRAMES)] # D

    delta_x = {} #E
    delta_y = {} #F
    delta_z = {} #G
    delta_r = {} #H
    thetas = {}  #I  

    for i in range(FRAMES):
        if i==0:
            continue
        temp_x = x_list[i] - x_list[i-1]
        temp_y = y_list[i] - y_list[i-1]
        temp_z = z_list[i] - z_list[i-1]
        temp_r = math.sqrt(temp_x**2+temp_y**2+temp_z**2)

        delta_x[i] = temp_x
        delta_y[i] = temp_y
        delta_z[i] = temp_z
        delta_r[i] = temp_r

        if i>1:
            dot_product = (delta_x[i]*delta_x[i-1] + delta_y[i]*delta_y[i-1] + delta_z[i]*delta_z[i-1])
            product_of_magnitudes = (delta_r[i]*delta_r[i-1])
            value = dot_product / (product_of_magnitudes + EPSILON)
            value = max(-1, min(1, value))
            temp_theta = math.acos(value)*180/math.pi
            thetas[i] = temp_theta

    # r          #J
    N1 = {}      #K
    # N2 = {}       #L
    Cr = {}      #M
    sigma = {}   #N
    logr = {}    #O
    logCr = {}   #P
    
    thresholds = [(i+1)/10 for i in range(FRAMES)]
    index_1 = thresholds.index(1)
    thresholds = thresholds[:index_1] + [1.01] + thresholds[(index_1+1):]
    thresholds[:20]

    for i in range(FRAMES):
        N1[i] = countif(list(delta_r.values()), thresholds[i])
        Cr[i] = N1[i] / (FRAMES - 1)

        try:
            logCr[i] = math.log10(Cr[i])
        except Exception as e:
            logger.error(f"At i = {i}, Cr[i] = {Cr[i]}")
            logger.error(f"Set Cr[i] to 10e-10")
            Cr[i] = 10e-10
            logCr[i] = math.log10(Cr[i])

        sigma[i] = math.log10(Cr[i])/math.log10(thresholds[i])
        logr[i] = math.log10(thresholds[i])

        

    APPROCH = 0.000
    neg_close = math.inf*(-1)
    neg_close_pos = -1
    for i, value in enumerate(list(logr.values())):
        if value < APPROCH and value > neg_close:
            neg_close = value
            neg_close_pos = i

    table_index = list(range(-5, 6))
    table_index.reverse()

    FD_df = pd.DataFrame(columns = ['number', 'logari', 'logariC', 'x-xbar', 'y-ybar', 
                            '(x-xbar)(y-ybar)', '(x-xbar)2', '(y-ybar)2', '[yi-(a+bxi)]2'])

    FD_df['number'] = table_index
    LEN = len(table_index)

    for row in range(LEN):
        num = table_index[row]
        num = num + neg_close_pos
        FD_df.iloc[row,1] = logr[num]                             # R
        FD_df.iloc[row,2] = logCr[num]                            # S

    col1 = np.array(list(FD_df['logari']))
    col2 = np.array(list(FD_df['logariC']))
    col1_avg = np.average(col1)                                     # average of R
    col2_avg = np.average(col2)                                     # average of S

    for row in range(LEN):
        FD_df.iloc[row,3] = FD_df.iloc[row,1] - col1_avg             # T
        FD_df.iloc[row,4] = FD_df.iloc[row,2] - col2_avg             # U
        FD_df.iloc[row,5] = FD_df.iloc[row,3] * FD_df.iloc[row,4]    # V
        FD_df.iloc[row,6] = FD_df.iloc[row,3]**2                     # W
        FD_df.iloc[row,7] = FD_df.iloc[row,4]**2                     # X

    #P4 =SUM(U16:U26)/SUM(V16:V26)
    #P5 =AVERAGE(Q16:Q26)-P4*AVERAGE(P16:P26)

    variable_b = np.sum(np.array(list(FD_df['(x-xbar)(y-ybar)']))) / np.sum(np.array(list(FD_df['(x-xbar)2'])))     # P4
    variable_a = col2_avg - col1_avg*variable_b                                                                     # P5

    # '[yi-(a+bxi)]2' =(Q16-($P$5+$P$4*P16))^2
    for row in range(LEN):
            FD_df.iloc[row,8] = (FD_df.iloc[row,2]-(variable_a+variable_b*FD_df.iloc[row,1]))**2     # Y
        
    #P6 =SQRT(SUM(X16:X26)/(COUNT(X16:X26)-2))
    variable_s = np.sqrt( np.sum(np.array(list(FD_df['[yi-(a+bxi)]2']))) / (LEN-2) )

    #R4 =P6/SQRT(SUM(V16:V26))
    variable_bErr = variable_s / np.sqrt(np.sum(np.array(list(FD_df['(x-xbar)2'])))) 

    #R5 =P6*SQRT((1/COUNT(X16:X26))+(AVERAGE(P16:P26)^2)/SUM(V16:V26))
    variable_aErr = variable_s*np.sqrt((1/LEN)+col1_avg**2/np.sum(np.array(list(FD_df['(x-xbar)2']))))

    #RR = =(SUM(U16:U26)^2)/(SUM(V16:V26)*SUM(W16:W26))
    variable_RR = np.sum(np.array(list(FD_df['(x-xbar)(y-ybar)'])))**2 / (np.sum(np.array(list(FD_df['(x-xbar)2']))) * np.sum(np.array(list(FD_df['(y-ybar)2']))))

    def get_entropy():
        G_array = np.array(list(thetas.values()))
        G_count = (G_array >= 90).sum()
        G_count2 = (G_array < 90).sum()
        G_len = G_array.size

        result = (-1) * G_count/G_len * np.log2(G_count/G_len) - G_count2/G_len * np.log2(G_count2/G_len)

        return result

    #H (Entropy)
    variable_Entropy = get_entropy()

    FractalDimension = variable_b
    Entropy = variable_Entropy

    return FractalDimension, Entropy