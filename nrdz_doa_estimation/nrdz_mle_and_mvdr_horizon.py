# This script uses both the maximum likelihood and MVDR algorithm to estimate the direction of arrival (DOA)
# Read the data from file or use test data generated by script
# Perform an FFT first
# Calculate sample covariance matrix for each frequency channel
# Estimate coordinates with minimum result from maximum likelihood output
# And estimate coordinates with maximum result from MVDR output for comparison in performance
# Specifically analysis of the horizon (90 degree elevation, azimuth cut)

import os
import sys
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import matrix_rank
from scipy import fftpack

# Size of real or imaginary data in file
#data_size = 20000000 # Large data size similar to real data
data_size = 2000 # Small data size for quick testing so you don't sit around waiting forever 
# Speed of light
c = 3e8
n_sources = 1 # Number of sources
src1_el = 90 #45 # First source's elevation
src1_az = 45 # First source's azimuth
ang_spread_el = 0 # 0.09 # The angle spread between sources in elevation
ang_spread_az = 50 # 0.09 # The angle spread between sources in azimuth
deg_range = 10000 # Number of coordinates being scanned/analyzed/plotted

center_el = 90 # Center elevation of map/field of view
center_az = 180 # Center azimuth of map/field of view
half_range = 180 # Half of the full range of coordinates on an axis
min_el = center_el - half_range # Minimum elevation along axis
max_el = center_el + half_range # Maximum elevation along axis
el_interval = (max_el-min_el)/(deg_range-1) # Interval between neighboring elevation coordinates. The minus 1 in the denominator is to accomodate the way linspace calculates the interval
min_az = center_az - half_range # Minimum azimuth along axis
max_az = center_az + half_range # Maximum azimuth along axis
az_interval = (max_az-min_az)/(deg_range-1) # Interval between neighboring azimuth coordinates. The minus 1 in the denominator is to accomodate the way linspace calculates the interval

# File path
filepath = "/mnt/datab-netStorage-1G/sync/"
# Extension of files
extension = ".sc16"

def coordinate_calculation(sensor_idx, sensor1_lat, sensor2_lat, deltaLat, deltaLng):
    # List of sensors other than north
    sensors = ["rooftop", "gate", "chime", "west", "nuevo"]
    
    # Calculate distance between points
    a = np.sin(deltaLat/2)*np.sin(deltaLat/2) + np.cos(sensor2_lat)*np.cos(sensor1_lat)*np.sin(deltaLng/2)*np.sin(deltaLng/2)
    c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
    R = 6371e3 # Radius of the earth in meters
    d = R*c

    print("Distance between north and " + sensors[sensor_idx] + " = " + str(d) + " meters")

    # Calculate bearing
    y = np.sin(deltaLng)*np.cos(sensor1_lat)
    x = np.cos(sensor2_lat)*np.sin(sensor1_lat) - np.sin(sensor2_lat)*np.cos(sensor1_lat)*np.cos(deltaLng)
    theta = np.arctan2(y, x)
    bearing = theta*180/np.pi

    print("Bearing of north to " + sensors[sensor_idx] + " = " + str(bearing))

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

    sensor_idx = 1
    r_gate = coordinate_calculation(sensor_idx, north_lat, gate_lat, deltaLat_ng, deltaLng_ng)
    
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
    
    sensor_idx = 2
    r_chime = coordinate_calculation(sensor_idx, north_lat, chime_lat, deltaLat_nc, deltaLng_nc)
    
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

    sensor_idx = 3
    r_west = coordinate_calculation(sensor_idx, north_lat, west_lat, deltaLat_nw, deltaLng_nw)
    
    return r_west

def north_nuevo_cartesian_estimates():
    # Sensor 5, North (Reference sensor)
    north_lat = 40.8216550*np.pi/180 #40.4902*np.pi/180
    north_lng = -121.4682424*np.pi/180 #121.2808*np.pi/180

    # Senor 7, nuevo
    nuevo_lat = 40.8242*np.pi/180 #40.4932*np.pi/180
    nuevo_lng = -121.4700*np.pi/180 #121.2812*np.pi/180

    # Change in latitude and longitude of north and rooftop
    deltaLat_nn = north_lat - nuevo_lat
    deltaLng_nn = north_lng - nuevo_lng

    sensor_idx = 4
    r_nuevo = coordinate_calculation(sensor_idx, north_lat, nuevo_lat, deltaLat_nn, deltaLng_nn)
    
    return r_nuevo

# Generate synthetic data
def synthetic_data(freq, tbin, rx, ry, rz):
    x_comp = np.zeros([data_size]) + 1j*np.zeros([data_size]) # Complex data array
    w = 2*np.pi*freq # Angular frequency
    s = np.zeros([data_size, n_sources]) + 1j*np.zeros([data_size, n_sources]) # Signal amplitude
    #a = np.zeros([n_sources]) + 1j*np.zeros([n_sources]) # Array steering vector
    el = np.zeros([data_size, n_sources]) # Elevation over time and of each source
    az = np.zeros([data_size, n_sources]) # Azimuth over time and of each source
    samp_el_offset = 0 # Change in elevation over time. Offsets signal position with a change in sample
    samp_az_offset = 0 # Change in azimuth over time. Offsets signal position with a change in sample
     
    #noise = np.random.normal(loc=0, scale=0.000000001, size=data_size) + 1j*np.random.normal(loc=0, scale=0.000000001, size=data_size)
    noise = np.random.normal(loc=0, scale=1, size=data_size) + 1j*np.random.normal(loc=0, scale=1, size=data_size)
    #noise = np.zeros([data_size]) + 1j*np.zeros([data_size]) 
    srcs = 0
    hpbw = 1
    A = 10
    second_sig_freq = 0 #200e3
    for t in range(0, data_size):
        srcs = 0
        prev_srcs = 0
        for p in range(0, n_sources):
            # Calculate el and az for each time sample of each source
            el[t,p] = (src1_el + (ang_spread_el*p) + samp_el_offset*t)*np.pi/180
            az[t,p] = (src1_az + (ang_spread_az*p) + samp_az_offset*t)*np.pi/180
            # Calculate ideal array steering vector using the array_manifold_vector() function
            if p == 0:
                w = 2*np.pi*freq
            elif p == 1:
                w = 2*np.pi*(freq+second_sig_freq)
            phase = (-1*w/c)*(\
            rx*np.sin(el[t,p])*np.cos(az[t,p])\
            + ry*np.sin(el[t,p])*np.sin(az[t,p])\
            + rz*np.cos(el[t,p]))
            s[t,p] = np.exp(1j*((w*t*tbin) + (phase%(2*np.pi))))
            #s[t,p] = np.sinc(freq*t*tbin)*np.exp(1j*phase)
            # ------------------Add noise---------------
            #A = np.exp(-2*(np.log(2)*pow(el[t,p],2)/pow(hpbw,2)))
            # Sum all source signals
            if p == 0:
                A = 100000
            elif p > 0:
                A = 100000
            srcs += A*s[t,p]
            
        # Assign srcs to signal vector
        #x_comp[t] = srcs + noise[t]
        x_comp[t] = srcs
        
    x_comp += noise
        
    # Check if signals are linearly independent
    #is_linearly_independent = np.all(np.linalg.det(np.vstack((s[0,:],s[1,:])).T) != 0)
    #print("Are the signals linearly independent? ", is_linearly_independent)

    return x_comp

# Generate synthetic data and write to binary file to test the code
def write_synthetic_data(filename, freq, tbin, rx, ry, rz, n_ants):
    x_comp = np.zeros([n_ants, data_size]) + 1j*np.zeros([n_ants, data_size]) # Complex data array
    x = np.zeros([2*data_size]).astype(np.int16) # Interleaved data array (real - even, imag - odd)
    full_filename = [""]*n_ants
    file_count = 0 # Count number of files generated
    
    # Generate synthetic data
    for i in range(0, n_ants):
        full_filename[i] = filepath + filename + str(i) + extension
        if not os.path.exists(full_filename[i]):
            x_comp[i,:] = synthetic_data(freq, tbin, rx[i], ry[i], rz[i])
            
            print("max x_comp["+ str(i) + "] = " + str(np.max(np.abs(x_comp[i,:]))))
            file_count += 1
        else:
            print("Test file, " + full_filename[i] + " exists so don't need to synthesize data, create, and write to it again.")
        
    # Convert elements in array to 16 bit integers the same way as with live data acquisition
    if file_count > 0:
        # Determine the maximum absolute value of the real and imaginary arrays
        max_int16 = 32767
        max_abs_value = np.max(np.abs(x_comp))
        scaling_factor = max_int16/max_abs_value
        scaled_x_comp = scaling_factor*x_comp
        arr_r = np.array(scaled_x_comp.real)
        scaled_arr_r = (arr_r).astype(np.int16)
        arr_i = np.array(scaled_x_comp.imag)
        scaled_arr_i = (arr_i).astype(np.int16)
    else:
        print("No conversion to 16 bits needed since no file need to be written.")
    
    for i in range(0, n_ants):
        if not os.path.exists(full_filename[i]):
            # Interleave real and imaginary components in array
            x[0:(2*data_size):2] = scaled_arr_r[i,:]
            x[1:(2*data_size):2] = scaled_arr_i[i,:]
            
            # Write data to binary file
            print("Writing to file, " + full_filename[i])
            with open(full_filename[i], 'wb') as f:
                f.write(x.tobytes())
            f.close()
        else:
            print(full_filename[i] + " exists.")

# Read file or generate test data 
def complex_data_sc16(data_flag, freq, tbin, filename, rx, ry, rz):
    if data_flag == 0: # Use test data
        data_comp = synthetic_data(freq, tbin, rx, ry, rz)
    elif data_flag == 1: # Read binary file
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                contents_nrdz = np.fromfile(f, dtype=np.int16)
                contents_size = len(contents_nrdz)
                # Interleave inphase and quadrature
                data_re = contents_nrdz[0:contents_size:2]
                data_im = contents_nrdz[1:contents_size:2]
                data_comp = data_re + 1j*data_im
        else:
            print("File, " + filename + " does not exist. Try another file.")
            print("Exiting...")
            sys.exit()
            
        f.close()
        
    return data_comp
    
# Perform FFT and return 2D array with dimensions, NSAMPS X NPOINTS
def perform_FFT(complex_data, n_points):
    data_len = len(complex_data)
    n_samps = int(data_len/n_points)
    data_fft = np.zeros([n_samps, n_points]) + 1j*np.zeros([n_samps, n_points]) 
    # Perform N-point FFT on data with dimensions, NSAMPS x NPOINTS
    for i in range(0, n_samps):
        #data_fft[i,:] = np.fft.fftshift(np.fft.fft(complex_data[(0+i*n_points):(n_points+i*n_points)]))
        data_fft[i,:] = (np.fft.fft(complex_data[(0+i*n_points):(n_points+i*n_points)]))
    
    return data_fft 

# Estimate sample covariance
def estimate_sample_covariance(x, n_ants, n_samps, n_points, n_ints):
    n_windows = int(n_samps/n_ints)
    if n_points > 1:
        R_est = np.zeros([n_ants, n_ants, n_samps, n_points]) + 1j*np.zeros([n_ants, n_ants, n_samps, n_points])
        R_hat = np.zeros([n_ants, n_ants, n_windows, n_points]) + 1j*np.zeros([n_ants, n_ants, n_windows, n_points])
    # Estimate covariance
    #for a in range(0, n_ants):
    #    for b in range(0, n_ants):
    #        R_est[a,b,:,:] = (np.multiply(x[a,:,:], np.conjugate(x[b,:,:])))
            
        for f in range(0, n_points):
            for t in range(0, n_samps):
                x_H = np.transpose(np.conj(x[:,t,f]))
                R_est[:,:,t,f] = (np.outer(x[:,t,f], x_H))
            
        # Integrate over time samples
        for i in range(0, n_windows):
            R_hat[:,:,i,:] = (1/n_ints)*np.sum(R_est[:,:,(0 + i*n_ints):((n_ints + i*n_ints)),:], axis=2)
    elif n_points == 1:
        R_est = np.zeros([n_ants, n_ants, n_samps]) + 1j*np.zeros([n_ants, n_ants, n_samps])
        R_hat = np.zeros([n_ants, n_ants, n_windows]) + 1j*np.zeros([n_ants, n_ants, n_windows])
    # Estimate covariance
    #for a in range(0, n_ants):
    #    for b in range(0, n_ants):
    #        R_est[a,b,:,:] = (np.multiply(x[a,:,:], np.conjugate(x[b,:,:])))

        for t in range(0, n_samps):
            x_H = np.transpose(np.conj(x[:,t]))
            R_est[:,:,t] = (np.outer(x[:,t], x_H))
            
        # Integrate over time samples
        for i in range(0, n_windows):
            R_hat[:,:,i] = (1/n_ints)*np.sum(R_est[:,:,(0 + i*n_ints):((n_ints + i*n_ints))], axis=2)
        
        
    return R_hat
    
# Calculate array manifold vector to use in MVDR solution
def array_manifold_vector(elevation, azimuth, rx, ry, rz, f, n_ants):
    # Angular frequency
    w = 2*np.pi*f
    #el = (src1_el-half_range + el_interval*elevation)*np.pi/180
    #az = (src1_az-half_range + az_interval*azimuth)*np.pi/180
    
    el = elevation*np.pi/180
    az = azimuth*np.pi/180
    
    a = np.zeros([n_ants,1]) + 1j*np.zeros([n_ants,1])
    
    # I believe I need to add the phase correction here
    # The phase added to remove the fringe function does not need to be added when live data or simulated earth rotation is NOT being read
    # But if earth is assumed to be rotating, the fringe function can be removed by adding a geometric delay to shift back to phase center by
    #    tau_geo = 
    #    where w_e = 7.3e-5 rad/s which is the angular rotation frequency of the earth
    # For the NRDZ sensors, the phase center cannot be chosen since they cannot be electronically steered. They are at fixed positions
    
    if n_ants == 1:
        for i in  range(0,n_ants):
            a[i] = np.exp((-1j*w/c)*(rx*np.sin(el)*np.cos(az) + ry*np.sin(el)*np.sin(az) + rz*np.cos(el)))
    else:
        for i in  range(0,n_ants):
            tau_instrumental = 0#(rx[i]*np.sin(src1_el)*np.cos(src1_az) + ry[i]*np.sin(src1_el)*np.sin(src1_az) + rz[i]*np.cos(src1_el))
            a[i] = np.exp((-1j*w/c)*((rx[i]*np.sin(el)*np.cos(az) + ry[i]*np.sin(el)*np.sin(az) + rz[i]*np.cos(el)) + tau_instrumental))
            if i == 2:
                tau = (rx[i]*np.sin(el)*np.cos(az) + ry[i]*np.sin(el)*np.sin(az) + rz[i]*np.cos(el))/c
        #print("tau of north chime baseline = " + str(tau))
    #print("tau instrumental = " + str(tau_instrumental))
    
    return a
    
def main():
    start_time = time.time()
    center_freq = 10e6
    freq = 11e6 # Frequency of signal (one of them if there are multiple at different frequencies) being detected
    #center_freq = 1e3
    samp_rate = 20e6#8*center_freq # Sample rate of synthesized signal
    tbin = 1/samp_rate # Time between samples
    full_band = samp_rate #20e6 # Full bandwidth in Hz
    n_points = 100 # Number of points of FFT
    coarse_chan = full_band/n_points
    #chan_idx = 50 # Narrowband frequency channe index - typically arbitrarily chosen to be at center of bandwidth
    narrowband_freqs = np.zeros([n_points,1])
    for c in range(0, n_points):
        if n_points > 1:
            f = center_freq + (c-n_points/2)*coarse_chan
            narrowband_freqs[c] = f
        elif n_points == 1:
            f = center_freq
    chan_idx = np.where(abs(narrowband_freqs-freq)==min(abs(narrowband_freqs-freq)))[0] # Narrowband frequency channe index
    print("Channel index = " + str(chan_idx[0]) + " of " + str(n_points))
    if data_size == 20000000:
        n_ints = 100 # Number of time samples to integrate
    elif data_size == 2000:
        if n_points == 500:
            n_ints = 4
        elif n_points == 100:
            n_ints = 20 # Number of time samples to integrate
        elif n_points == 1:
            n_ints = 100
    else:
        n_ints = 1 # Number of time samples to integrate
    n_samps = int(data_size/n_points) # Number of time samples after FFT
    
    print("Calculating cartesian coordiantes...")
    
    array_flag = 0 # Flag to run either current nrdz sensor array or ideal nrdz sensor array
                   # 0 -> NRDZ 6 sensor array
                   # 1 -> NRDZ ideal array with similar sized aperture
                   # 2 -> Standard phased array based on set number of antennas in variable "n_ants"
    if array_flag == 0:
        n_ants = 6 # Number of sensors/antennas
        print("Array flag is set to 0 for current NRDZ 6 sensor array")
        # Get cartesian coordinates between sensors
        r_rooftop = north_rooftop_cartesian_estimates()
        r_gate = north_gate_cartesian_estimates()
        r_chime = north_chime_cartesian_estimates()
        r_west = north_west_cartesian_estimates()
        r_nuevo = north_nuevo_cartesian_estimates()
        coordinate_scaling = 1
        if n_ants == 6:
            rx = np.zeros(n_ants)
            rx[0] = 0
            rx[1] = r_rooftop[0]/coordinate_scaling
            rx[2] = r_gate[0]/coordinate_scaling
            rx[3] = r_chime[0]/coordinate_scaling
            rx[4] = r_west[0]/coordinate_scaling
            rx[5] = r_nuevo[0]/coordinate_scaling
            ry = np.zeros(n_ants)
            ry[0] = 0
            ry[1] = r_rooftop[1]/coordinate_scaling
            ry[2] = r_gate[1]/coordinate_scaling
            ry[3] = r_chime[1]/coordinate_scaling
            ry[4] = r_west[1]/coordinate_scaling
            ry[5] = r_nuevo[1]/coordinate_scaling
            rz = np.zeros(n_ants)
            print("Rooftop X and Y coordinates respectively: " + str(rx[1]) + " m and " + str(ry[1]) + " m")
            print("Gate X and Y coordinates respectively: " + str(rx[2]) + " m and " + str(ry[2]) + " m")
            print("Chime X and Y coordinates respectively: " + str(rx[3]) + " m and " + str(ry[3]) + " m")
            print("West X and Y coordinates respectively: " + str(rx[4]) + " m and " + str(ry[4]) + " m")
            print("Nuevo X and Y coordinates respectively: " + str(rx[5]) + " m and " + str(ry[5]) + " m")
    elif array_flag == 1:
        print("Array flag is set to 1 for ideal NRDZ sensor array with the same longest baseline as the current")
        longest_baseline = np.sqrt(np.square(abs(r_gate[0]) + abs(r_chime[0])) + np.square(abs(r_gate[1]) + abs(r_chime[1])))
        print("The longest baseline = " + str(longest_baseline) + " meters")
        wavelength = (c/center_freq)
        antenna_array_dimension = round(longest_baseline/(wavelength/2))
        n_ants = np.sqrt(antenna_array_dimension)
        rx = np.zeros(n_ants)
        ry = np.zeros(n_ants)
        rz = np.zeros(n_ants)
        for x in range(0,antenna_array_dimension):
            for y in range(0,antenna_array_dimension):
                rx[y + (x*antenna_array_dimension)] = (x-(antenna_array_dimension/2))*(wavelength/2)
                ry[y + (x*antenna_array_dimension)] = (y-(antenna_array_dimension/2))*(wavelength/2)
    elif array_flag == 2:
        n_ants = 49 # Number of sensors/antennas
        print("Array flag is set to 2 for the standard phased array based on set number of antennas in variable n_ants")
        scale_baseline = 1
        wavelength = (c/center_freq)
        rx = np.zeros(n_ants)
        ry = np.zeros(n_ants)
        rz = np.zeros(n_ants)
        antenna_array_dimension = np.sqrt(n_ants)
        for x in range(0,int(antenna_array_dimension)):
            for y in range(0,int(antenna_array_dimension)):
                rx[y + (x*int(antenna_array_dimension))] = (x-int(antenna_array_dimension/2))*(wavelength/2)*scale_baseline
                ry[y + (x*int(antenna_array_dimension))] = (y-int(antenna_array_dimension/2))*(wavelength/2)*scale_baseline
    
    data_flag = 0 # If set to 0, the script generates it's own data, and if set to 1, it reads a file
    sim_data_write = 1 # If set to 1, the script synthesizes data and writes it to a binary file to be read, and if set to 0, the simulated data is not written to and read from binary files
    
    filename = "sensor_test_"
    full_filename = [""]*n_ants
    
    # Synthesize test data if flag is set to 1
    if sim_data_write == 1:
        print("Writing data to files...")
        data_flag = 1
        write_synthetic_data(filename, freq, tbin, rx, ry, rz, n_ants)
    else:
        print("Simulated data has not been written to any files. It has just been generated and processed by the script.")
    
    print("Reading data for processing...")
    if n_points > 1:
        X_agg = np.zeros([n_ants, n_samps, n_points]) + 1j*np.zeros([n_ants, n_samps, n_points])
    elif n_points == 1:
        X_agg = np.zeros([n_ants, n_samps]) + 1j*np.zeros([n_ants, n_samps])
        
    # Read/generate data, perform FFT and aggregate sensor data 
    for i in range(0, n_ants):
        full_filename[i] = filepath + filename + str(i) + extension
        # Read or generate complex data
        x = complex_data_sc16(data_flag, freq, tbin, full_filename[i], rx[i], ry[i], rz[i])
        if n_points > 1:
            # Perform FFT
            Xfft = perform_FFT(x, n_points)
            # Aggregate sensor data
            X_agg[i,:,:] = Xfft
        elif n_points == 1:
            # Aggregate sensor data
            X_agg[i,:] = x
    
    print("Estimating sample covariance matrix...")
    # Estimate sample covariance
    R_hat = estimate_sample_covariance(X_agg, n_ants, n_samps, n_points, n_ints)
    
    # Estimate power spectrum over elevation and azimuth
    R_x = np.zeros([n_ants, n_ants]) + 1j*np.zeros([n_ants, n_ants])
    if n_points > 1:
        R_x = R_hat[:,:,0,chan_idx[0]]
        f = center_freq + (chan_idx[0]-n_points/2)*coarse_chan
    elif n_points == 1:
        chan_idx = 0
        R_x = R_hat[:,:,0]
        f = center_freq
        
    print(R_x)
    
    
    print("Determine the maximum number of sources that can be localized.")
    print("-------------------------------------------")
    print("This is not necessarily relevant for basic MVDR since only one source can be localized at a particular frequency channel so you may skip this if uninterested.")
    print("-------------------------------------------")
    print("The max number of sources, P, detected is limited by the rank of the covariance matrix estimate, R, and the number of sensors, M")
    print("If the sources are uncorrelated implying R = P, then the following conditions are satisfied:")
    print("If P < (M+R)/2, then all of the sources can be uniquiely localized for every batch of data.")
    print("And a weaker condition, if P < 2RM/(2R+1), then for almost every batch, except for batches that have a measure of zero, these sources can be uniquely localized. This is a weaker condition in the sense that if P is at least less than 2RM/(2R+1), then the sources will be localized in most batches (not every batch) of data.")
    print("If the sources are fully correlated, R = 1, then unique localization (uniqueness) is ensured if P < (M+1)/2, and a weaker less stringent condition, P < 2M/3.")
    rank_R = matrix_rank(R_x)
    print("Rank of estimated covariance matrix, R, is " + str(rank_R))
    print("Number of sensors, M, is " + str(n_ants))
    
    a = np.zeros([n_ants,1])
    a_H = np.zeros([1,n_ants])
    beam_el = center_el
    beam_az = center_az
    a_center = array_manifold_vector(beam_el, beam_az, rx, ry, rz, f, n_ants)
    a_second = array_manifold_vector(beam_el+ang_spread_el, beam_az+ang_spread_az, rx, ry, rz, f, n_ants)
    P = np.zeros([n_ants,n_ants])
    Ld = np.zeros([deg_range,n_points])
    ld = np.zeros([deg_range,n_points])
    P_est = np.zeros([deg_range,n_points])
    ld_normalized = np.zeros([deg_range,n_points])
    mvdr_normalized = np.zeros([deg_range,n_points])
    spectra = np.zeros([n_points,1])
    synthesized_beam = np.zeros([deg_range,n_points])
    #synthesized_beam1 = np.zeros([deg_range,1])
    az_range = np.linspace(min_az, max_az,deg_range) # Range of azimuth
    print("center_frequency = " + str(center_freq) + " f = " + str(f))
    
    print("Estimating power spectrum...")
    el = center_el
    full_spectrum = 1 # 0 -> Don't save or plot full spectrum to save computation time
                      # 1 -> Plot 3 bins surrounding the one with the signal to save computation time
                      # 2 -> Plot full spectrum
    if full_spectrum == 0:
        if n_points > 1:
            R_x = R_hat[:,:,0,chan_idx[0]]
            f = center_freq + (chan_idx[0]-n_points/2)*coarse_chan
        elif n_points == 1:
            R_x = R_hat[:,:,0]
            f = center_freq
        for az in range(0,deg_range):
            #a = array_manifold_vector(el, az, rx, ry, rz, f, n_ants)
            a = array_manifold_vector(el, az_range[az], rx, ry, rz, f, n_ants)
            a_H = np.transpose(np.conjugate(a))
            a_center_H = np.transpose(np.conjugate(a_center))
            a_second_H = np.transpose(np.conjugate(a_second))
            a_H_a = np.matmul(a_H,a)
            A_pinv = (1/a_H_a)*a_H
            P = np.matmul(a,A_pinv)
            P_perp = np.eye(n_ants,n_ants) - P
            # Maximum Likelihood
            Ld[az,chan_idx[0]] = -1*np.log(np.trace(abs(np.matmul(P_perp,R_x))))
            ld[az,chan_idx[0]] = np.trace(abs(np.matmul(P_perp,R_x)))
            # MVDR
            P_den = abs(np.dot(np.dot(a_H,np.linalg.inv(R_x)), a))
            P_est[az,chan_idx[0]] = 1/P_den
            beam_coordinate = np.matmul(a_center_H, a)[0]
            synthesized_beam[az,chan_idx[0]] = np.square(abs(beam_coordinate[0]))
            #beam_coordinate1 = np.matmul(a_second_H, a)[0]
            #synthesized_beam1[az,0] = np.square(abs(beam_coordinate1[0]))
            #P_den = abs(a_H.dot(np.linalg.inv(R_x)).dot(a))
            #P_den = abs(a_H.dot(np.linalg.inv(np.eye(n_ants,n_ants))).dot(a))
            #P_den = abs(np.dot(np.dot(a_H,np.linalg.inv(R_x)), a))
            #P[el,az] = 1/P_den
        max_mle = np.max(1/ld[:,chan_idx[0]])
        ld_normalized[:,chan_idx[0]] = (1/max_mle)*(1/ld[:,chan_idx[0]])
        max_mvdr = np.max(P_est[:,chan_idx[0]])
        mvdr_normalized[:,chan_idx[0]] = (1/max_mvdr)*P_est[:,chan_idx[0]]
    elif full_spectrum == 1:
        print("Minimum channel index = " + str(chan_idx[0]-1))
        print("Maximum channel index = " + str(chan_idx[0]+1))
        for c in range(chan_idx[0]-1, chan_idx[0]+2):
            print("Frequency bin " + str(c) + " of " + str(n_points))
            if n_points > 1:
                R_x = R_hat[:,:,0,c]
                f = center_freq + (c-n_points/2)*coarse_chan
            elif n_points == 1:
                R_x = R_hat[:,:,0]
                f = center_freq
            spectra[c] = abs(np.matmul(np.matmul(np.ones([1,n_ants]),R_x),np.ones([n_ants,1])))
            for az in range(0,deg_range):
                #a = array_manifold_vector(el, az, rx, ry, rz, f, n_ants)
                a = array_manifold_vector(el, az_range[az], rx, ry, rz, f, n_ants)
                a_H = np.transpose(np.conjugate(a))
                a_center_H = np.transpose(np.conjugate(a_center))
                a_second_H = np.transpose(np.conjugate(a_second))
                a_H_a = np.matmul(a_H,a)
                A_pinv = (1/a_H_a)*a_H
                P = np.matmul(a,A_pinv)
                P_perp = np.eye(n_ants,n_ants) - P
                # Maximum Likelihood
                Ld[az,c] = -1*np.log(np.trace(abs(np.matmul(P_perp,R_x))))
                ld[az,c] = np.trace(abs(np.matmul(P_perp,R_x)))
                # MVDR
                P_den = abs(np.dot(np.dot(a_H,np.linalg.inv(R_x)), a))
                P_est[az,c] = 1/P_den
                beam_coordinate = np.matmul(a_center_H, a)[0]
                synthesized_beam[az,c] = np.square(abs(beam_coordinate[0]))
                #beam_coordinate1 = np.matmul(a_second_H, a)[0]
                #synthesized_beam1[az,0] = np.square(abs(beam_coordinate1[0]))
                #P_den = abs(a_H.dot(np.linalg.inv(R_x)).dot(a))
                #P_den = abs(a_H.dot(np.linalg.inv(np.eye(n_ants,n_ants))).dot(a))
                #P_den = abs(np.dot(np.dot(a_H,np.linalg.inv(R_x)), a))
                #P[el,az] = 1/P_den
            max_mle = np.max(1/ld[:,c])
            ld_normalized[:,c] = (1/max_mle)*(1/ld[:,c])
            max_mvdr = np.max(P_est[:,c])
            mvdr_normalized[:,c] = (1/max_mvdr)*P_est[:,c]
    elif full_spectrum == 2:
        display_bin = 0
        range_bins = 20
        for c in range(0, n_points):
            if c == (display_bin*range_bins):
                print("Frequency bin " + str(c) + " of " + str(n_points))
                display_bin += 1
            if n_points > 1:
                R_x = R_hat[:,:,0,c]
                f = center_freq + (c-n_points/2)*coarse_chan
            elif n_points == 1:
                R_x = R_hat[:,:,0]
                f = center_freq
            spectra[c] = abs(np.matmul(np.matmul(np.ones([1,n_ants]),R_x),np.ones([n_ants,1])))
            for az in range(0,deg_range):
                #a = array_manifold_vector(el, az, rx, ry, rz, f, n_ants)
                a = array_manifold_vector(el, az_range[az], rx, ry, rz, f, n_ants)
                a_H = np.transpose(np.conjugate(a))
                a_center_H = np.transpose(np.conjugate(a_center))
                a_second_H = np.transpose(np.conjugate(a_second))
                a_H_a = np.matmul(a_H,a)
                A_pinv = (1/a_H_a)*a_H
                P = np.matmul(a,A_pinv)
                P_perp = np.eye(n_ants,n_ants) - P
                # Maximum Likelihood
                Ld[az,c] = -1*np.log(np.trace(abs(np.matmul(P_perp,R_x))))
                ld[az,c] = np.trace(abs(np.matmul(P_perp,R_x)))
                # MVDR
                P_den = abs(np.dot(np.dot(a_H,np.linalg.inv(R_x)), a))
                P_est[az,c] = 1/P_den
                beam_coordinate = np.matmul(a_center_H, a)[0]
                synthesized_beam[az,c] = np.square(abs(beam_coordinate[0]))
                #beam_coordinate1 = np.matmul(a_second_H, a)[0]
                #synthesized_beam1[az,0] = np.square(abs(beam_coordinate1[0]))
                #P_den = abs(a_H.dot(np.linalg.inv(R_x)).dot(a))
                #P_den = abs(a_H.dot(np.linalg.inv(np.eye(n_ants,n_ants))).dot(a))
                #P_den = abs(np.dot(np.dot(a_H,np.linalg.inv(R_x)), a))
                #P[el,az] = 1/P_den
            max_mle = np.max(1/ld[:,c])
            ld_normalized[:,c] = (1/max_mle)*(1/ld[:,c])
            max_mvdr = np.max(P_est[:,c])
            mvdr_normalized[:,c] = (1/max_mvdr)*P_est[:,c]
    
    # Find the index of the azimuth angles corresponding to a particular source
    az1_idx = np.where(abs(az_range-src1_az)==min(abs(az_range-src1_az)))[0]
    az2_idx = np.where(abs(az_range-(src1_az+ang_spread_az))==min(abs(az_range-(src1_az+ang_spread_az))))[0]
    print("Size of a = " + str(a.shape))
    print("Size of a^H = " + str(a_H.shape))
    print("Size of a^H*a = " + str(a_H_a.shape))
    print("Size of A_pinv = " + str(A_pinv.shape))        
    print("Size of P perp = " + str(P_perp.shape))
    print("Size of P = " + str(P.shape))
    
    print("Plotting...")
    # Plot the synthesized beam
    plt.figure()
    plt.plot(az_range, synthesized_beam[0:deg_range,chan_idx[0]])
    plt.title("Synthesized beam (dirty beam) over elevation at " + str(narrowband_freqs[chan_idx[0]][0]/1e6) + " MHz")
    plt.ylabel("Power (arb. units)")
    plt.xlabel("Azimuth (degrees)")
    plt.show()
    
    # Plot map of power estimate at a particular coarse channel
    #plt.figure()
    #plt.plot(az_range, Ld[0:deg_range])
    #plt.title("Maximum likelihood estimate over elevation at " + str(narrowband_freqs[chan_idx[0]][0]/1e6) + " MHz")
    #plt.ylabel("Likelihood result (dB)")
    #plt.xlabel("Azimuth (degrees)")
    #plt.show()
    
    #plt.figure()
    #plt.plot(az_range, ld[0:deg_range])
    #plt.title("Maximum likelihood estimate over elevation at El = " + str(el) + " deg")
    #plt.ylabel("Likelihood result (arb. units)")
    #plt.xlabel("Azimuth (degrees)")
    #plt.show()
    
    #plt.figure()
    #plt.plot(az_range, 10*np.log10(P_est[0:deg_range]))
    #plt.title("MVDR estimate over elevation at El = " + str(el) + " deg")
    #plt.ylabel("Power (dB)")
    #plt.xlabel("Azimuth (degrees)")
    #plt.show()
    
    #plt.figure()
    #plt.plot(az_range, P_est[0:deg_range])
    #plt.title("MVDR estimate over elevation at El = " + str(el) + " deg")
    #plt.ylabel("Power (arb. units)")
    #plt.xlabel("Azimuth (degrees)")
    #plt.show()
    
    plt.figure()
    plt.plot(az_range, ld_normalized[0:deg_range,chan_idx[0]], label='MLE')
    plt.plot(az_range, mvdr_normalized[0:deg_range,chan_idx[0]], label='MVDR')
    plt.title("MLE and MVDR estimate along the horizon at " + str(narrowband_freqs[chan_idx[0]][0]/1e6) + " MHz")
    plt.ylabel("Power (Normalized)")
    plt.xlabel("Azimuth (degrees)")
    plt.legend()
    plt.show()
    
    az_theta = np.linspace(0,2*np.pi, deg_range)
    plt.figure()
    plt.polar(az_theta, ld_normalized[0:deg_range,chan_idx[0]], label='MLE')
    plt.polar(az_theta, mvdr_normalized[0:deg_range,chan_idx[0]], label='MVDR')
    plt.title("MLE and MVDR estimate along the horizon at " + str(narrowband_freqs[chan_idx[0]][0]/1e6) + " MHz")
    plt.ylabel("Power (Normalized)")
    plt.xlabel("Azimuth (degrees)")
    plt.legend(loc='upper left')
    plt.show()
    
    if full_spectrum == 1:
        if n_points > 1:
            plt.figure()
            plt.plot(narrowband_freqs[(chan_idx[0]-1):(chan_idx[0]+2)]/1e6, spectra[(chan_idx[0]-1):(chan_idx[0]+2)])
            plt.title("Average spectra over the sensor array")
            plt.ylabel("Power (arb. units)")
            plt.xlabel("Frequency (MHz)")
            plt.show()
    if full_spectrum == 2:
        if n_points > 1:
            plt.figure()
            plt.plot(narrowband_freqs/1e6, spectra)
            plt.title("Average spectra over the sensor array")
            plt.ylabel("Power (arb. units)")
            plt.xlabel("Frequency (MHz)")
            plt.show()

    end_time = time.time()
    execution_time = end_time-start_time
    print("Execution time = " + str(execution_time) + " seconds")
    print("Done!")

if __name__ == "__main__":
    main()





