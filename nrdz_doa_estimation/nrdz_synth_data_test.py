import sys
import os
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Size of real or imaginary data in file
#data_size = 20000000 # Large data size similar to real data
data_size = 2000 # Small data size for quick testing so you don't sit around waiting forever
# Time between samples
tbin = 1/data_size
# Speed of light
c = 3e8

def coordinate_calculation(sensor1_lat, sensor2_lat, deltaLat, deltaLng):
    # Calculate distance between points
    a = np.sin(deltaLat/2)*np.sin(deltaLat/2) + np.cos(sensor2_lat)*np.cos(sensor1_lat)*np.sin(deltaLng/2)*np.sin(deltaLng/2)
    c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
    R = 6371e3 # Radius of the earth in meters
    d = R*c

    print("Distance between north and gate = " + str(d) + " meters")

    # Calculate bearing
    y = np.sin(deltaLng)*np.cos(sensor1_lat)
    x = np.cos(sensor2_lat)*np.sin(sensor1_lat) - np.sin(sensor2_lat)*np.cos(sensor1_lat)*np.cos(deltaLng)
    theta = np.arctan2(y, x)
    bearing = theta*180/np.pi

    print("Bearing of sensor 1 to sensor 2 = " + str(bearing))

    # Calculate x and y coordinates between north and gate in meters
    x_m = d*np.sin(theta)
    y_m = d*np.cos(theta)
    
    r = np.zeros(2)
    r[0] = x_m
    r[1] = y_m
    
    return r

def north_rooftop_cartesian_estimates():
    # Sensor 5, North (Reference sensor)
    north_lat = 40.8216550*np.pi/180 #40.4902*np.pi/180
    north_lng = -121.4682424*np.pi/180 #121.2808*np.pi/180

    # Senor 2, Rooftop
    rooftop_lat = 40.8172*np.pi/180 #40.4932*np.pi/180
    rooftop_lng = -121.469*np.pi/180 #121.2812*np.pi/180

    # Change in latitude and longitude of north and rooftop
    deltaLat_nr = north_lat - rooftop_lat
    deltaLng_nr = north_lng - rooftop_lng

    sensor_idx = 0
    r_rooftop = coordinate_calculation(sensor_idx, north_lat, rooftop_lat, deltaLat_nr, deltaLng_nr)
    
    return r_rooftop

def north_gate_cartesian_estimates():
    # Sensor 5, North (Reference sensor)
    north_lat = 40.8216550*np.pi/180 #40.4902*np.pi/180
    north_lng = -121.4682424*np.pi/180 #121.2808*np.pi/180

    # Senor 2, Gate
    gate_lat = 40.8257948*np.pi/180 #40.4932*np.pi/180
    gate_lng = -121.4702578*np.pi/180 #121.2812*np.pi/180

    # Change in latitude and longitude of north and gate
    deltaLat_ng = north_lat - gate_lat
    deltaLng_ng = north_lng - gate_lng

    r_gate = coordinate_calculation(north_lat, gate_lat, deltaLat_ng, deltaLng_ng)
    
    return r_gate    
    
def north_chime_cartesian_estimates():
    # Sensor 5, North (Reference sensor)
    north_lat = 40.8216550*np.pi/180 #40.4902*np.pi/180
    north_lng = -121.4682424*np.pi/180 #121.2808*np.pi/180

    # Sensor 3, Chime
    chime_lat = 40.8166504*np.pi/180 #40.4859*np.pi/180
    chime_lng = -121.4639321*np.pi/180 #121.2750*np.pi/180

    # Change in latitude and longitude of north and chime
    deltaLat_nc = north_lat - chime_lat
    deltaLng_nc = north_lng - chime_lng
    
    r_chime = coordinate_calculation(north_lat, chime_lat, deltaLat_nc, deltaLng_nc)
    
    return r_chime
    
def north_west_cartesian_estimates():
    # Sensor 5, North (Reference sensor)
    north_lat = 40.8216550*np.pi/180 #40.4902*np.pi/180
    north_lng = -121.4682424*np.pi/180 #121.2808*np.pi/180

    # Sensor 4, West
    west_lat = 40.8167476*np.pi/180 #40.4900*np.pi/180
    west_lng = -121.4720492*np.pi/180 #121.2819*np.pi/180
    
    # Change in latitude and longitude of west and gate
    deltaLat_nw = north_lat - west_lat
    deltaLng_nw = north_lng - west_lng

    r_west = coordinate_calculation(north_lat, west_lat, deltaLat_nw, deltaLng_nw)
    
    return r_west
    
# Calculate array manifold vector to use in MVDR solution
def array_manifold_vector(elevation, azimuth, rx, ry, rz, f, n_ants):
    # Angular frequency
    w = 2*np.pi*f
    el = elevation*180/np.pi
    az = azimuth*180/np.pi
    
    a = np.zeros(n_ants)
    
    if n_ants == 1:
        for i in  range(0,n_ants):
            a[i] = np.exp((-1j*w/c)*(rx*np.sin(el)*np.cos(az) + rz*np.sin(el)*np.sin(az) + rz*np.cos(el)))
    else:
        for i in  range(0,n_ants):
            a[i] = np.exp((-1j*w/c)*(rx[i]*np.sin(el)*np.cos(az) + rz[i]*np.sin(el)*np.sin(az) + rz[i]*np.cos(el)))
    
    return a
    
# Estimate sample covariance
def estimate_sample_covariance(x, n_ants, n_samps, n_points, n_ints):
    n_windows = int(n_samps/n_ints)
    R_est = np.zeros([n_ants, n_ants, n_samps, n_points])
    R_hat = np.zeros([n_ants, n_ants, n_windows, n_points])
    # Estimate covariance
    for a in range(0, n_ants):
        for b in range(0, n_ants):
            R_est[a,b,:,:] = abs(np.multiply(x[a,:,:], np.conjugate(x[b,:,:])))
    
    # Integrate over time samples
    for i in range(0, n_windows):
        R_hat[:,:,i,:] = (1/n_ints)*np.sum(R_est[:,:,(0 + i*n_ints):((n_ints + i*n_ints)),:], axis=2)
        
    return R_hat

# Perform FFT and return 2D array with dimensions, NSAMPS X NPOINTS
def perform_FFT(complex_data, n_points):
    data_len = len(complex_data)
    n_samps = int(data_len/n_points)
    data_fft = np.zeros([n_samps, n_points]) + 1j*np.zeros([n_samps, n_points]) 
    # Perform N-point FFT on data with dimensions, NSAMPS x NPOINTS
    for i in range(0, n_samps):
        data_fft[i,:] = np.fft.fft(complex_data[(0+i*n_points):(n_points+i*n_points)])
    
    return data_fft

freq = 1e3 #200e6
full_band = 20e6 # Full bandwidth in Hz
n_points = 100 # Number of points of FFT
n_ants = 5 # Number of sensors/antennas
if data_size == 20000000:
    n_ints = 100 # Number of time samples to integrate
elif data_size == 2000:
    n_ints = 10 # Number of time samples to integrate
else:
    n_ints = 1 # Number of time samples to integrate
n_samps = int(data_size/n_points) # Number of time samples after FFT
    
print("Calculating cartesian coordiantes...")
# Get cartesian coordinates between sensors
r_gate = north_gate_cartesian_estimates()
r_chime = north_chime_cartesian_estimates()
r_west = north_west_cartesian_estimates()
rx = np.zeros(n_ants)
rx[0] = 0
rx[1] = r_gate[0]
rx[2] = r_chime[0]
rx[3] = r_west[0]
ry = np.zeros(n_ants)
ry[0] = 0
ry[1] = r_gate[1]
ry[2] = r_chime[1]
ry[3] = r_west[1]
rz = np.zeros(n_ants)

x_comp = np.zeros([data_size]).astype(np.int16) + 1j*np.zeros([data_size]).astype(np.int16) # Complex data array
#x_comp = np.zeros([data_size]) + 1j*np.zeros([data_size]) # Complex data array
w = 2*np.pi*freq # Angular frequency
n_sources = 1 # Number of sources
s = np.zeros([n_sources]) # Signal amplitude
a = np.zeros([n_sources]) # Array steering vector
el = np.zeros([data_size, n_sources]) # Elevation over time and of each source
az = np.zeros([data_size, n_sources]) # Azimuth over time and of each source
src1_el = 45 # First source's elevation
src1_az = 45 # First source's azimuth
ang_spread = 20 # The angle spread between sources
samp_el_offset = 0 # Change in elevation over time. Offsets signal position with a change in sample
samp_az_offset = 0 # Change in azimuth over time. Offsets signal position with a change in sample 
    
srcs = 0
print("Calculating simulated signal")
i = 0 # Antenna element index
for t in range(0, data_size):
    srcs = 0
    for p in range(0, n_sources):
        # Calculate el and az for each time sample of each source
        el[t,p] = (src1_el + (ang_spread*p) + samp_el_offset*t)*np.pi/180
        az[t,p] = (src1_az + (ang_spread*p) + samp_az_offset*t)*np.pi/180
        # Calculate ideal array steering vector using the array_manifold_vector() function
        a[p] = array_manifold_vector(el[t,p], az[t,p], rx[i],ry[i],rz[i],freq,1)
        # Calulate signal amplitude over time (plane wave)
        s[p] = np.sin((w*(t*tbin))%(2*np.pi))
        # ------------------Add noise---------------
        # Sum all source signals
        srcs += s[p]*a[p]
        # Assign srcs to signal vector
        x_comp[t] = srcs

# Convert elements in array to 16 bit integers the same way as with live data acquisition
max_int16 = 32767
max_abs_value = np.max(np.abs(x_comp))
scaling_factor = max_int16/max_abs_value
scaled_x_comp = scaling_factor*x_comp
arr_r = np.array(scaled_x_comp.real)
scaled_arr_r = (arr_r).astype(np.int16)
arr_i = np.array(scaled_x_comp.imag)
scaled_arr_i = (arr_i).astype(np.int16)

#min_dbl = -3.4e38
#max_dbl = 3.4e38
#arr_r = np.array(x_comp.real)
#scaled_arr_r = np.interp(arr_r, (min_dbl, max_dbl), (-32768,32767)).astype(np.int16)
#arr_i = np.array(x_comp.imag)
#scaled_arr_i = np.interp(arr_i, (min_dbl, max_dbl), (-32768,32767)).astype(np.int16)

x = np.zeros([2*data_size]).astype(np.int16) # Interleaved data array (real - even, imag - odd)
#x = np.zeros([2*data_size]) # Interleaved data array (real - even, imag - odd)
# Interleave real and imaginary components in array
x[0:(2*data_size):2] = scaled_arr_r
x[1:(2*data_size):2] = scaled_arr_i
#x[0:(2*data_size):2] = x_comp.real
#x[1:(2*data_size):2] = x_comp.imag

complex_data = scaled_arr_r + 1j*scaled_arr_i
#complex_data = x_comp.real + 1j*x_comp.imag

# Perform FFT
Xfft = perform_FFT(complex_data, n_points)

print("Complex values")
print(x_comp[0])
print(x_comp[10])
print(x_comp[100])
print(x_comp[1000])

print("Interleaved complex after int 16")
print(x[0])
print(x[1])
print(x[10])
print(x[11])
print(x[100])
print(x[101])
print(x[1000])
print(x[1001])

print("Plotting absolute value of complex data...")
# Plot map of power estimate at a particular coarse channel
plt.figure()
plt.plot(abs(x_comp))
plt.title("Amplitude of complex samples (for testing)")
plt.ylabel("Arb. units")
plt.xlabel("Time samples")
plt.show()

print("Plotting absolute value of FFT...")
# Plot map of power estimate at a particular coarse channel
plt.figure()
plt.imshow(abs(Xfft), extent=[0, n_points, 0, n_samps], aspect='auto', interpolation='none')
plt.title("Waterfall plot of amplitudes after FFT")
plt.ylabel("Time samples")
plt.xlabel("N-points")
plt.show()
