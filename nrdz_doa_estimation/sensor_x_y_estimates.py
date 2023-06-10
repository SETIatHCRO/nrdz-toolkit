print("This script calculates the distance in cartesian coordinates between the refernce NRDZ antenna/sensor (north) to the 3 other sensors that are up on site.")
print("")
print("Map of sensors at site and theta (th) in this starts at the vertical bars, |")
print("")
print("            2")
print("")
print("")
print("")
print("")
print("                5")
print("               /|")
print("              / |")
print("             /  |")
print("            / <-|")
print("           / th |")
print("        4       |")
print("                |        3")
print("")
print("Sensor 1 is not up currently")
print("Sensor 2 is Gate")
print("Sensor 3 is Chime")
print("Sensor 4 is West")
print("Sensor 5 is North")
print("")
print("Equations found here: movable-type.co.uk/scripts/latlong.html")
print("")
# This script calculates the distance in cartesian coordinates between the refernce NRDZ antenna/sensor (north) to the 3 other sensors that are up on site.
# Map of sensors at site and theta (th) in this starts at the vertical bars, |
#
#            2
#     
#
#
#
#                5
#               /|
#              / |
#             /  |
#            / <-|
#           / th |
#        4       |
#                |        3
#                
# Sensor 1 is not up currently
# Sensor 2 is Gate
# Sensor 3 is Chime
# Sensor 4 is West
# Sensor 5 is North
#
# Equations found here: movable-type.co.uk/scripts/latlong.html

import numpy as np

# Sensor 5, North (Reference sensor)
north_lat = 40.8216550*np.pi/180 #40.4902*np.pi/180
north_lng = -121.4682424*np.pi/180 #121.2808*np.pi/180

# Senor 2, Gate
gate_lat = 40.8257948*np.pi/180 #40.4932*np.pi/180
gate_lng = -121.4702578*np.pi/180 #121.2812*np.pi/180

# Sensor 3, Chime
chime_lat = 40.8166504*np.pi/180 #40.4859*np.pi/180
chime_lng = -121.4639321*np.pi/180 #121.2750*np.pi/180

# Sensor 4, West
west_lat = 40.8167476*np.pi/180 #40.4900*np.pi/180
west_lng = -121.4720492*np.pi/180 #121.2819*np.pi/180

R = 6371e3 # Radius of the earth in meters

# Change in latitude and longitude of north and gate
deltaLat_ng = north_lat - gate_lat
deltaLng_ng = north_lng - gate_lng

# Calculate distance between points
a_ng = np.sin(deltaLat_ng/2)*np.sin(deltaLat_ng/2) + np.cos(gate_lat)*np.cos(north_lat)*np.sin(deltaLng_ng/2)*np.sin(deltaLng_ng/2)
c_ng = 2*np.arctan2(np.sqrt(a_ng),np.sqrt(1-a_ng))
d_ng = R*c_ng

print("Distance between north and gate = " + str(d_ng) + " meters")

# Calculate bearing
y_ng = np.sin(deltaLng_ng)*np.cos(north_lat)
x_ng = np.cos(gate_lat)*np.sin(north_lat) - np.sin(gate_lat)*np.cos(north_lat)*np.cos(deltaLng_ng)
theta_ng = np.arctan2(y_ng, x_ng)
bearing_ng = theta_ng*180/np.pi

print("Bearing of north to gate = " + str(bearing_ng))

# Calculate x and y coordinates between north and gate in meters
x_m_ng = d_ng*np.sin(theta_ng)
y_m_ng = d_ng*np.cos(theta_ng)

print("X distance north|gate = " + str(x_m_ng) + " meters")
print("Y distance north|gate = " + str(y_m_ng) + " meters")

print("")

# Change in latitude and longitude of north and chime
deltaLat_nc = north_lat - chime_lat
deltaLng_nc = north_lng - chime_lng

# Calculate distance between points
a_nc = np.sin(deltaLat_nc/2)*np.sin(deltaLat_nc/2) + np.cos(chime_lat)*np.cos(north_lat)*np.sin(deltaLng_nc/2)*np.sin(deltaLng_nc/2)
c_nc = 2*np.arctan2(np.sqrt(a_nc),np.sqrt(1-a_nc))
d_nc = R*c_nc

print("Distance between north and chime = " + str(d_nc) + " meters")

# Calculate bearing
y_nc = np.sin(deltaLng_nc)*np.cos(north_lat)
x_nc = np.cos(chime_lat)*np.sin(north_lat) - np.sin(chime_lat)*np.cos(north_lat)*np.cos(deltaLng_nc)
theta_nc = np.arctan2(y_nc, x_nc)
bearing_nc = theta_nc*180/np.pi

print("Bearing of north to chime = " + str(bearing_nc))

# Calculate x and y coordinates between north and chime in meters
x_m_nc = d_nc*np.sin(theta_nc)
y_m_nc = d_nc*np.cos(theta_nc)

print("X distance north|chime = " + str(x_m_nc) + " meters")
print("Y distance north|chime = " + str(y_m_nc) + " meters")

print("")

# Change in latitude and longitude of west and gate
deltaLat_nw = north_lat - west_lat
deltaLng_nw = north_lng - west_lng

# Calculate distance between points
a_nw = np.sin(deltaLat_nw/2)*np.sin(deltaLat_nw/2) + np.cos(west_lat)*np.cos(north_lat)*np.sin(deltaLng_nw/2)*np.sin(deltaLng_nw/2)
c_nw = 2*np.arctan2(np.sqrt(a_nw),np.sqrt(1-a_nw))
d_nw = R*c_nw

print("Distance between north and west = " + str(d_nw) + " meters")

# Calculate bearing
y_nw = np.sin(deltaLng_nw)*np.cos(north_lat)
x_nw = np.cos(west_lat)*np.sin(north_lat) - np.sin(west_lat)*np.cos(north_lat)*np.cos(deltaLng_nw)
theta_nw = np.arctan2(y_nw, x_nw)
bearing_nw = theta_nw*180/np.pi

print("Bearing of north to west = " + str(bearing_nw))

# Calculate x and y coordinates between north and west in meters
x_m_nw = d_nw*np.sin(theta_nw)
y_m_nw = d_nw*np.cos(theta_nw)

print("X distance north|west = " + str(x_m_nw) + " meters")
print("Y distance north|west = " + str(y_m_nw) + " meters")
