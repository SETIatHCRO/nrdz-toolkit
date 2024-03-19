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

# Size of real/imaginary data in file
#data_size = 20000000 # Large data size similar to real data
data_size = 2000 # Small data size for quick testing so you don't sit around waiting forever 
# Speed of light
c = 3e8
n_sources = 1 # Number of sources
src1_el = 90 #45 # First source's elevation
src1_az = 335 # First source's azimuth
ang_spread_el = 0 # 0.09 # The angle spread between sources in elevation
ang_spread_az = 35 # 0.09 # The angle spread between sources in azimuth
deg_range = 10000 # Number of coordinates being scanned/analyzed/plotted

# Source x and y coordinates from reference antenna
rs_x = 10
rs_y = 20
rs_z = 0

# Range of source values to sweep through
x_range = 20
y_range = 30
z_range = 0

ant_center_freq = 1e9 # 1e5
ant_freq = 1e9 # 1e5+1e6 # Frequency of signal (one of them if there are multiple at different frequencies) being detected
ant_f_down = 0 #1e3 # Shift frequency down if signal frequency is high and baselines are very long
samp_rate = 20e6 #20e6 # Sample rate of synthesized signal
n_points = 1 # Number of points of FFT
tbin = 1/samp_rate # Time between samples
full_band = samp_rate #20e6 # Full bandwidth in Hz
coarse_chan = full_band/n_points
tbin_fft = 1/coarse_chan

radio_interferomters = ["NRDZ-sensors", "ATA"] # Show these options in help command
array_conf = radio_interferomters[0] # Input from User. 

center_el = 90 # Center elevation of map/field of view
center_az = 180 # Center azimuth of map/field of view
half_range = 180 # Half of the full range of coordinates on an axis
min_el = center_el - (half_range/4) # Minimum elevation along axis
max_el = center_el + (half_range/4) # Maximum elevation along axis
el_interval = (max_el-min_el)/(deg_range-1) # Interval between neighboring elevation coordinates. The minus 1 in the denominator is to accomodate the way linspace calculates the interval
min_az = center_az - half_range # Minimum azimuth along axis
max_az = center_az + half_range # Maximum azimuth along axis
az_interval = (max_az-min_az)/(deg_range-1) # Interval between neighboring azimuth coordinates. The minus 1 in the denominator is to accomodate the way linspace calculates the interval

# File path
#filepath = "/mnt/primary-1G/test/"
#filepath = "/home/sonata/src/nrdz_toolkit/nrdz_doa_estimation/output/"
filepath = "/mnt/local_data/nrdz_test/"
# Extension of files
extension = ".sc16"


def parabolic_reflector_radiation_pattern(diameter, wavelength, azimuth, elevation):
    A = np.sinc((np.pi*diameter*np.sin(azimuth*np.pi/180)*np.cos(elevation*np.pi/180)/wavelength))
    
    return A

if array_conf == radio_interferomters[0]:
    ant_pattern = lambda ant_wavelength: 10 # Isotropic antenna

    reference_ant = {"north": [40.8216550, -121.4682424]}

    antennas = {"rooftop": [40.8172, -121.469], 
    "gate": [40.8257948, -121.4702578], 
    "chime": [40.8166504, -121.4639321], 
    "west": [40.8167476, -121.4720492], 
    "nuevo": [40.8242, -121.4700]}

elif array_conf == radio_interferomters[1]:
    ant_diameter = 6.1
    #ant_wavelength = c/ant_freq
    ant_elevation = 0
    ant_azimuth = 90
    ant_pattern = lambda ant_wavelength: parabolic_reflector_radiation_pattern(ant_diameter, ant_wavelength, ant_azimuth, ant_elevation)
    
    reference_ant = {"1a": [40.816712869598824, -121.47104786441923]}
    
    antennas = {"1b": [40.81656164962182, -121.47064246433446],
    "1c": [40.81598672956708, -121.47073316425822],
    "1d": [40.816020919548556, -121.47101366431262],
    "1e": [40.816118279542216, -121.47118336435452],
    "1f": [40.81610954951161, -121.47153176440668],
    "1g": [40.81629270952532, -121.47153856443505],
    "1h": [40.81642770951056, -121.47183376450059],
    "1j": [40.81683078953103, -121.47195666457858],
    "1k": [40.816714109574605, -121.47133636446472],
    "2a": [40.81743072968048, -121.47073476447545],
    "2b": [40.81733629969617, -121.47046306441914],
    "2c": [40.81708831967276, -121.47051706439166],
    "2d": [40.81689592969735, -121.4700501642903],
    "2e": [40.81692103971665, -121.46984496426194],
    "2f": [40.8170445795826, -121.4715439645459],
    "2g": [40.81702735955206, -121.47188836459696],
    "2h": [40.81713778956801, -121.47180126459976],
    "2j": [40.81727308959045, -121.47165746459687],
    "2k": [40.81732482960396, -121.47154386458651],
    "2l": [40.817330509629556, -121.47124826454152],
    "2m": [40.81731489966026, -121.47087376448117],
    "3c": [40.817723089775875, -121.46987526438447],
    "3d": [40.81792499974508, -121.47042396449997],
    "3e": [40.81782593971099, -121.47073826453484],
    "3f": [40.817715489686485, -121.47092576454763],
    "3g": [40.81769358967525, -121.4710387645621],
    "3h": [40.81777863968334, -121.47100596456677],
    "3j": [40.81812358976585, -121.47035936451907],
    "3l": [40.81830225975086, -121.47070116459905],
    "4e": [40.8179877798225, -121.4695646643747],
    "4f": [40.81815999978997, -121.47010756448512],
    "4g": [40.818336179775734, -121.47043646456237],
    "4h": [40.8183644197648, -121.47059216459104],
    "4j": [40.818545549820264, -121.47009796453975],
    "4k": [40.81831159981528, -121.46994726448243],
    "4l": [40.8183095098262, -121.4698188644626],
    "5b": [40.8182326298965, -121.46891176430843],
    "5c": [40.81807838989098, -121.46883596427385],
    "5e": [40.81800398989564, -121.46871006424269],
    "5g": [40.817955419865314, -121.46902806428588],
    "5h": [40.818073009877175, -121.468994864298]}


ref_ant_name = list(reference_ant.keys())
antenna_names = list(antennas.keys())
#print(antennas[antenna_names[0]][0])

# Number of antennas
n_ants = len(antenna_names)+1


def coordinate_calculation(ref_lat, ant_lat, deltaLat, deltaLng):
    xy_coords = {}
    
    # Calculate distance between points
    R = 6371e3 # Radius of the earth in meters
    for ant in range(0,len(antenna_names)):
        a = np.sin(deltaLat[ant]/2)*np.sin(deltaLat[ant]/2) + np.cos(ant_lat[ant])*np.cos(ref_lat)*np.sin(deltaLng[ant]/2)*np.sin(deltaLng[ant]/2)
        c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
        d = R*c

        # Calculate bearing
        y_bearing = np.sin(deltaLng[ant])*np.cos(ref_lat)
        x_bearing = np.cos(ant_lat[ant])*np.sin(ref_lat) - np.sin(ant_lat[ant])*np.cos(ref_lat)*np.cos(deltaLng[ant])
        theta = np.arctan2(y_bearing, x_bearing)
        bearing = theta*180/np.pi

        # Calculate x and y coordinates between reference and other antenna in meters
        x = d*np.sin(theta)
        y = d*np.cos(theta)
        
        # Store x and y baseline in dictionary
        lat = antennas[antenna_names[ant]][0]
        lng = antennas[antenna_names[ant]][1]
        xy_coords[antenna_names[ant],lat,lng] = [x, y]
    
    return xy_coords

def cartesian_estimates():
    # Reference antenna
    ref_lat = reference_ant[ref_ant_name[0]][0]*np.pi/180
    ref_lng = reference_ant[ref_ant_name[0]][1]*np.pi/180

    # Antenna
    ant_lat = [antennas[ant][0]*np.pi/180 for ant in antenna_names]
    ant_lng = [antennas[ant][1]*np.pi/180 for ant in antenna_names]

    # Change in latitude and longitude of reference antenna and other
    deltaLat = [ref_lat - ant_lat[l] for l in range(0,len(ant_lat))]
    deltaLng = [ref_lng - ant_lng[l] for l in range(0,len(ant_lng))]

    # x and y coordinate estimates
    xy_coords = {}
    xy_coords[ref_ant_name[0],reference_ant[ref_ant_name[0]][0],reference_ant[ref_ant_name[0]][1]] = [0,0]
    xy_coords.update(coordinate_calculation(ref_lat, ant_lat, deltaLat, deltaLng))
    
    return xy_coords

# Generate synthetic data
def synthetic_data(sim_freq, tbin, rx, ry, rz):
    x_comp = np.zeros([data_size], dtype=complex) # Complex data array
    w = 2*np.pi*sim_freq # Angular frequency
    s = np.zeros([data_size, n_sources], dtype=complex) # Signal amplitude
    #a = np.zeros([n_sources]) + 1j*np.zeros([n_sources]) # Array steering vector
    el = np.zeros([data_size, n_sources]) # Elevation over time and of each source
    az = np.zeros([data_size, n_sources]) # Azimuth over time and of each source
    samp_el_offset = 0 # Change in elevation over time. Offsets signal position with a change in sample
    samp_az_offset = 0 # Change in azimuth over time. Offsets signal position with a change in sample
     
    #noise = np.random.normal(loc=0, scale=0.000000001, size=data_size, dtype=complex)
    noise = np.random.normal(loc=0, scale=1, size=data_size) + 1j*np.random.normal(loc=0, scale=1, size=data_size)
    srcs = 0
    hpbw = 1
    A = 10
    second_sig_freq = 0 #200e3
    window_counter = 0
    for t in range(0, data_size):
        srcs = 0
        prev_srcs = 0
        for p in range(0, n_sources):
            # Calculate el and az for each time sample of each source
            el[t,p] = (src1_el + (ang_spread_el*p) + samp_el_offset*t)*np.pi/180
            az[t,p] = (src1_az + (ang_spread_az*p) + samp_az_offset*t)*np.pi/180
            # Calculate ideal array steering vector using the array_manifold_vector() function
            if p == 0:
                w = 2*np.pi*sim_freq
            elif p == 1:
                w = 2*np.pi*(sim_freq+second_sig_freq)
            phase = (-1*w/c)*(\
            (rx+rs_x)*np.sin(el[t,p])*np.cos(az[t,p])\
            + (ry+rs_y)*np.sin(el[t,p])*np.sin(az[t,p])\
            + (rz+rs_z)*np.cos(el[t,p]))
            #s[t,p] = np.exp(1j*((w*t*tbin) + (phase%(2*np.pi))))
            #s[t,p] = np.exp(1j*((w*t*tbin) + (phase)))
            #s[t,p] = np.sinc(w*t*tbin)*np.exp(1j*phase)
            
            tau = (1/c)*(\
            (rx+rs_x)*np.sin(el[t,p])*np.cos(az[t,p])\
            + (ry+rs_y)*np.sin(el[t,p])*np.sin(az[t,p])\
            + (rz+rs_z)*np.cos(el[t,p]))
            #if (t*tbin) >= abs(tau):
            #    window_counter += 1
            #    if window_counter < 30:
            #        s[t,p] = np.exp(1j*((w*t*tbin) + (phase)))
            
            tau_idx = int(np.floor(tau/tbin))
            #print(tau_idx)
            
            signal_start_time_idx = 400
            window_counter += 1
            if window_counter < 30:
                s[signal_start_time_idx+(t+tau_idx),p] = np.exp(1j*((w*t*tbin) + (phase)))
            
            # ------------------Add noise---------------
            #A = np.exp(-2*(np.log(2)*pow(el[t,p],2)/pow(hpbw,2)))
            # Sum all source signals
            #if p == 0:
            #    A = 10
            #elif p > 0:
            #    A = 10
            ant_lambda = c/sim_freq
            A = ant_pattern(ant_lambda)
            srcs += A*s[t,p]
            
        # Assign srcs to signal vector
        #x_comp[t] = srcs + noise[t]
        x_comp[t] = srcs
        
    x_comp += noise
    
    #print("tbin = " + str(tbin))
    #print("tau = " + str(tau))
    
    # Check if signals are linearly independent
    #is_linearly_independent = np.all(np.linalg.det(np.vstack((s[0,:],s[1,:])).T) != 0)
    #print("Are the signals linearly independent? ", is_linearly_independent)

    return x_comp

# Generate synthetic data and write to binary file to test the code
def write_synthetic_data(filename, sim_freq, tbin, rx, ry, rz, n_ants):
    x_comp = np.zeros([n_ants, data_size], dtype=complex) # Complex data array
    x = np.zeros([2*data_size]).astype(np.int16) # Interleaved data array (real - even, imag - odd)
    full_filename = [""]*n_ants
    file_count = 0 # Count number of files generated
    
    # Generate synthetic data
    for i in range(0, n_ants):
        #print("ant = " + str(i))
        full_filename[i] = filepath + filename + str(i) + extension
        if not os.path.exists(full_filename[i]):
            x_comp[i,:] = synthetic_data(sim_freq, tbin, rx[i], ry[i], rz[i])
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
def complex_data_sc16(data_flag, sim_freq, tbin, filename, rx, ry, rz):
    if data_flag == 0: # Use test data
        data_comp = synthetic_data(sim_freq, tbin, rx, ry, rz)
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
    data_fft = np.zeros([n_samps, n_points], dtype=complex) 
    # Perform N-point FFT on data with dimensions, NSAMPS x NPOINTS
    for i in range(0, n_samps):
        data_fft[i,:] = np.fft.fftshift(np.fft.fft(complex_data[(0+i*n_points):(n_points+i*n_points)]))
        #data_fft[i,:] = (np.fft.fft(complex_data[(0+i*n_points):(n_points+i*n_points)]))
    
    return data_fft 

# Estimate visibilities (cross correlations)
def estimate_visibilities(x, n_ants, n_samps):
    vis = np.asarray([np.multiply(x[n,:],np.conj(x[m,:])) for n in range(0, n_ants) for m in range(0, n_ants) if n!=m])
    #print("Visibility shape = " + str(np.shape(vis)))
    
    return vis
    
# Estimate visibilities (cross correlations)
def estimate_visibility_pairs(x, ant_1, ant_2, n_ants, n_samps):
    vis = np.multiply(x[ant_1,:],np.conj(x[ant_2,:]))
    #print("Visibility shape = " + str(np.shape(vis)))
    
    return vis
    
# Estimate visibilities (cross correlations)
def estimate_cross_correlations(x, n_ants):
    # Compute length for zero-padding
    N = len(x[0,:]) + len(x[1,:]) - 1
    
    r = {}
    for n in range(0,n_ants):
        for m in range(0,n_ants):
            if n!=m or (n == 0 and m == 0):
                # Perform zero-padding to ensure lengths match for FFT
                ant1_padded = np.pad(x[n,:], (0, N-len(x[n,:])), mode='constant')
                ant2_padded = np.pad(x[m,:], (0, N-len(x[m,:])), mode='constant')
    
                # Compute FFT of signals
                A1 = np.fft.fft(ant1_padded)
                A2 = np.fft.fft(ant2_padded)
    
                # Compute complex conjugate of FFT of A1
                A1_conj = np.conj(A1)
    
                # Element-wise multiplication in frequency domain
                R = A1_conj*A2
    
                # Compute inverse FFT to get cross-correlation in time domain
                r[n, m] = np.fft.fftshift(np.fft.ifft(R))
    
    return r
    
# Estimate visibilities (cross correlations)
def estimate_cross_correlations_traditional(x, n_ants):
    # Compute length for zero-padding
    L = len(x[0,:]) + len(x[1,:]) - 1
    
    cross_corr = np.zeros(L,dtype=complex)
    
    r = {}
    for n in range(0,n_ants):
        for m in range(0,n_ants):
            if n!=m:
                # Reverse second antenna vector
                y_rev = np.flipud(x[n,:])
                
                # Perform convolution
                for l in range(L):
                    # Determine range of valide indices for convolution
                    start_index = max(0, l-len(x[n,:])+1)
                    end_index = min(len(x[m,:]), l+1)
                    
                    for k in range(start_index, end_index):
                        cross_corr[l] += x[m,k]*np.conj(y_rev[l-k])
    
                # Compute inverse FFT to get cross-correlation in time domain
                r[n, m] = cross_corr
    
    return r
    
# Estimate visibilities (cross correlations)
def estimate_cross_correlation_pairs(x, ant_1, ant_2, n_ants, n_samps):
    # Compute length for zero-padding
    N = len(x[ant_1,:]) + len(x[ant_2,:]) - 1
    
    # Perform zero-padding to ensure lengths match for FFT
    ant1_padded = np.pad(x[ant_1,:], (0, N-len(x[ant_1,:])), mode='constant')
    ant2_padded = np.pad(x[ant_2,:], (0, N-len(x[ant_2,:])), mode='constant')
    
    # Compute FFT of signals
    A1 = np.fft.fft(ant1_padded)
    A2 = np.fft.fft(ant2_padded)
    
    # Compute complex conjugate of FFT of A1
    A1_conj = np.conj(A1)
    
    # Element-wise multiplication in frequency domain
    R = A1_conj*A2
    
    # Compute inverse FFT to get cross-correlation in time domain
    r = np.fft.fftshift(np.fft.ifft(R))
    
    return r
    
# Estimate auto correlations
def estimate_auto_correlations(x, n_ants, n_samps):
    autos = np.asarray([np.multiply(x[n,:],np.conj(x[m,:])) for n in range(0, n_ants) for m in range(0, n_ants) if n==m])
    #print("Autos shape = " + str(np.shape(autos)))
    
    return autos

# Calculate phase shift to use in synthesis imaging
def interferometric_phase_shift(elevation, azimuth, rx, ry, rz, f, n_ants):
    # Angular frequency
    w = 2*np.pi*f
    #el = (src1_el-half_range + el_interval*elevation)*np.pi/180
    #az = (src1_az-half_range + az_interval*azimuth)*np.pi/180
    
    el = elevation*np.pi/180
    az = azimuth*np.pi/180
    
    if n_ants == 1:
        sys.exit("You have to set more than one antenna")
    else:
        a = np.asarray([np.exp((-1j*w/c)*(((rx[m]-rx[n])*np.sin(el)*np.cos(az) + (ry[m]-ry[n])*np.sin(el)*np.sin(az) + (rz[m]-rz[n])*np.cos(el)))) for n in range(0,n_ants) for m in range(0,n_ants) if n!=m])
    
    #print("Phase shift vector shape = " + str(np.shape(a)))
    
    return a
    
# Estimate sample covariance
def estimate_sample_covariance(x, n_ants, n_samps, n_points, n_ints):
    n_windows = int(n_samps/n_ints)
    if n_points > 1:
        R_est = np.zeros([n_ants, n_ants, n_samps], dtype=complex)
        R_hat = np.zeros([n_ants, n_ants, n_windows], dtype=complex)
        
        for t in range(0, n_samps):
            x_H = np.transpose(np.conj(x[:,t]))
            R_est[:,:,t] = (np.outer(x[:,t], x_H))
            
        # Integrate over time samples
        for i in range(0, n_windows):
            R_hat[:,:,i] = (1/n_ints)*np.sum(R_est[:,:,(0 + i*n_ints):((n_ints + i*n_ints))], axis=2)
    elif n_points == 1:
        R_est = np.zeros([n_ants, n_ants, n_samps], dtype=complex)
        R_hat = np.zeros([n_ants, n_ants, n_windows], dtype=complex)

        for t in range(0, n_samps):
            x_H = np.transpose(np.conj(x[:,t]))
            R_est[:,:,t] = (np.outer(x[:,t], x_H))
            
        # Integrate over time samples
        for i in range(0, n_windows):
            R_hat[:,:,i] = (1/n_ints)*np.sum(R_est[:,:,(0 + i*n_ints):((n_ints + i*n_ints))], axis=2)

    return R_hat
    
# Calculate array manifold vector to use in MVDR solution
def array_manifold_vector(elevation, azimuth, rx, ry, rz, f, n_ants, mix_down, t):
    # Angular frequency
    w = 2*np.pi*f
    
    el = elevation*np.pi/180
    az = azimuth*np.pi/180
    
    a = np.zeros([n_ants,1], dtype=complex)
    
    # I believe I need to add the phase correction here
    # The phase added to remove the fringe function does not need to be added when live data or simulated earth rotation is NOT being read
    # But if earth is assumed to be rotating, the fringe function can be removed by adding a geometric delay to shift back to phase center by
    #    tau_geo = 
    #    where w_e = 7.3e-5 rad/s which is the angular rotation frequency of the earth
    # For the NRDZ sensors, the phase center cannot be chosen since they cannot be electronically steered. They are at fixed positions
    
    if n_ants == 1:
        sys.exit("You have to set more than one antenna")
    else:
        for i in  range(0,n_ants):
            a[i] = np.exp((-1j*w/c)*((rx[i]*np.sin(el)*np.cos(az) + ry[i]*np.sin(el)*np.sin(az) + rz[i]*np.cos(el))))
    
    return a


def main():
    start_time = time.time()
    center_freq = ant_center_freq
    freq = ant_freq # Frequency of signal (one of them if there are multiple at different frequencies) being detected
    #center_freq = 1e3
    #chan_idx = 50 # Narrowband frequency channe index - typically arbitrarily chosen to be at center of bandwidth
    narrowband_freqs = np.zeros([n_points,1])
    for ch in range(0, n_points):
        if n_points > 1:
            f = center_freq + (ch-n_points/2)*coarse_chan
            narrowband_freqs[ch] = f
        elif n_points == 1:
            f = center_freq
            narrowband_freqs[ch] = f
    chan_idx = np.where(abs(narrowband_freqs-freq)==min(abs(narrowband_freqs-freq)))[0] # Narrowband frequency channel index
    print("Channel index = " + str(chan_idx[0]) + " of " + str(n_points))
    if data_size == 20000000:
        n_ints = 100 # Number of time samples to integrate
    elif data_size == 2000:
        if n_points == 1000:
            n_ints = 2
        elif n_points == 500:
            n_ints = 4
        elif n_points == 100:
            n_ints = 20 # Number of time samples to integrate
        elif n_points == 1:
            n_ints = 100
    else:
        n_ints = 1 # Number of time samples to integrate
    n_samps = int(data_size/n_points) # Number of time samples after FFT
    
    print("Calculating cartesian coordiantes...")

    # x and y coordinate estimates
    ant_rect_coords = {}
    ant_rect_coords = cartesian_estimates()
    
    # Store cartesian estimates
    rx = np.zeros(n_ants)
    ry = np.zeros(n_ants)
    rz = np.zeros(n_ants)
    rx = np.asarray([ant_rect_coords[xy][0] for xy in ant_rect_coords])
    ry = np.asarray([ant_rect_coords[xy][1] for xy in ant_rect_coords])
    #print(rx)
    #print(ry)
    
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
        X_agg = np.zeros([n_ants, n_samps, n_points], dtype=complex)
    elif n_points == 1:
        X_agg = np.zeros([n_ants, n_samps], dtype=complex)
        
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
    
    az_range = np.linspace(min_az, max_az,deg_range) # Range of azimuth
    el = center_el
    
    print(X_agg.shape)
    
    # Frequency of signal at narrowband frequency channel
    if n_points > 1:
        f = center_freq + (chan_idx[0]-n_points/2)*coarse_chan
    
    spectra = np.zeros([n_points,1])
    tau = {}
    #synthesized_beam1 = np.zeros([deg_range,1])
    
    print("center_frequency = " + str(center_freq) + " f = " + str(f))
    
    print("Estimating power spectrum...")
    
    full_spectrum = 0 # 0 -> Don't save or plot full spectrum to save computation time
                      # 1 -> Plot 3 bins surrounding the one with the signal to save computation time
                      # 2 -> Plot full spectrum
    if full_spectrum == 0:
        freq_chan_indices = [chan_idx[0]]
    elif full_spectrum == 1:
        print("Minimum channel index = " + str(chan_idx[0]-1))
        print("Maximum channel index = " + str(chan_idx[0]+1))
        freq_chan_indices = range(chan_idx[0]-1, chan_idx[0]+2)
    elif full_spectrum == 2:
        display_bin = 0
        range_bins = 20
        freq_chan_indices = range(0, n_points)
    
    az_rad = az_range*np.pi/180
    el_rad = el*np.pi/180
    est_x_src = np.array([])
    est_y_src = np.array([])
    est_az_src = np.array([])
    num_indices = 4
    per_baseline_closest_x = np.array([])
    per_baseline_closest_y = np.array([])
    per_baseline_closest_az = np.array([])
    tau = {}
    for ch in freq_chan_indices:
        if n_points > 1:
            f = center_freq + (ch-n_points/2)*coarse_chan
            Vis = estimate_cross_correlations(X_agg[:,:,ch], n_ants)
        elif n_points == 1:
            f = center_freq
            Vis = estimate_cross_correlations(X_agg[:,:], n_ants)

        auto_corr = abs(Vis[0,0])
        auto_corr_peak_time_idx = np.argmax(auto_corr)
        for n in range(0,n_ants):
            for m in range(0,n_ants): 
                if n!=m:
                    x_corr = abs(Vis[n,m])
                    max_val_time_idx = np.argmax(x_corr)
                    calc_delay = (max_val_time_idx-auto_corr_peak_time_idx)*tbin_fft
                    
                    print("n=" + str(n) + " m=" + str(m) + " max_val_time_idx = " + str(max_val_time_idx))
                    print("n=" + str(n) + " m=" + str(m) + " max_val_time_idx-auto_corr_peak_time_idx = " + str(max_val_time_idx-auto_corr_peak_time_idx))
                    print("calc_delay = " + str(calc_delay))
                    
                    #for xs in range(0,x_range):
                    #    for ys in range(0,y_range):
                    #        for az in range(0,deg_range):
                    #            tau[xs,ys,az_range[az]] = (-1/c)*((((rx[n]-rx[m])+xs)*np.sin(el_rad)*np.cos(az_rad[az]) + ((ry[n]-ry[m])+ys)*np.sin(el_rad)*np.sin(az_rad[az]) + (rz[n]-rz[m])*np.cos(el_rad)))
                    
                    tau = {(xs,ys,az_range[az]):(-1/c)*((((rx[n]-rx[m])-xs)*np.sin(el_rad)*np.cos(az_rad[az]) + ((ry[n]-ry[m])-ys)*np.sin(el_rad)*np.sin(az_rad[az]) + (rz[n]-rz[m])*np.cos(el_rad))) for az in range(0,deg_range) for ys in range(0,y_range) for xs in range(0,x_range)}
                    
                    tau_values = np.array(list(tau.values()))
                    tau_keys = np.array(list(tau.keys()))
                    
                    range_az_closest_indices = np.argsort(abs(tau_values-calc_delay))
                    closest_indices = range_az_closest_indices[:num_indices]
                    #print(tau_keys[closest_indices])
                    for idx in range(0,num_indices):
                        est_x_src = np.concatenate((est_x_src,np.array([tau_keys[closest_indices][idx][0]])), axis=0)
                        est_y_src = np.concatenate((est_y_src,np.array([tau_keys[closest_indices][idx][1]])), axis=0)
                        est_az_src = np.concatenate((est_az_src,np.array([tau_keys[closest_indices][idx][2]])), axis=0)
                    
                    per_baseline_closest_x = np.concatenate((per_baseline_closest_x,est_x_src),axis=0)
                    per_baseline_closest_y = np.concatenate((per_baseline_closest_y,est_y_src),axis=0)
                    per_baseline_closest_az = np.concatenate((per_baseline_closest_az,est_az_src),axis=0)

    #np.savetxt("tau.txt", tau)
    unique_x,counts_x = np.unique(per_baseline_closest_x.astype(int), return_counts=True)
    max_count_idx_x = np.argmax(counts_x)
    est_x_range_tdoa_tmp = unique_x[counts_x==counts_x[max_count_idx_x]]
    est_x_range_tdoa = np.mean(est_x_range_tdoa_tmp)
    
    unique_y,counts_y = np.unique(per_baseline_closest_y.astype(int), return_counts=True)
    max_count_idx_y = np.argmax(counts_y)
    est_y_range_tdoa_tmp = unique_y[counts_y==counts_y[max_count_idx_y]]
    est_y_range_tdoa = np.mean(est_y_range_tdoa_tmp)
    
    unique_az,counts = np.unique(per_baseline_closest_az.astype(int), return_counts=True)
    max_count_idx = np.argmax(counts)
    est_az_angle_tdoa_tmp = unique_az[counts==counts[max_count_idx]]
    est_az_angle_tdoa = np.mean(est_az_angle_tdoa_tmp)
    
    print("Estimated x range from mode = " + str(est_x_range_tdoa_tmp))
    print("Estimated x range after mean of mode = " + str(est_x_range_tdoa))
    
    print("Estimated y range from mode = " + str(est_y_range_tdoa_tmp))
    print("Estimated y range after mean of mode = " + str(est_y_range_tdoa))
    
    print("Estimated az angle from mode = " + str(est_az_angle_tdoa_tmp))
    print("Estimated az angle after mean of mode = " + str(est_az_angle_tdoa))
    
    #calc_az_avg = calc_az_avg/((n_ants*n_ants)-n_ants)
    #print("calc_az_avg = " + str(calc_az_avg))
    #tau_avg = tau_avg/((n_ants*n_ants)-n_ants)
    #z_scalar_avg = z_scalar_avg/((n_ants*n_ants)-n_ants)
    #sci_avg = sci_avg/((n_ants*n_ants)-n_ants)
    #est_az_rad = np.arccos(tau_avg/z_scalar_avg)-sci_avg
    #est_az = est_az_rad*180/np.pi
    #print("Estimated az = " + str(est_az))
    
    #print(x_corr.shape)
    print("Plotting...")
    
    fig, axs = plt.subplots(6)
    axs[0].plot(abs(X_agg[0,:]))
    axs[0].set_title("Amplitude of antenna voltage")
    axs[0].set_ylabel("Power (arb. units)")
    
    axs[1].plot(abs(X_agg[1,:]))
    axs[1].set_ylabel("Power (arb. units)")
    
    axs[2].plot(abs(X_agg[2,:]))
    axs[2].set_ylabel("Power (arb. units)")
    
    axs[3].plot(abs(X_agg[3,:]))
    axs[3].set_ylabel("Power (arb. units)")
    
    axs[4].plot(abs(X_agg[4,:]))
    axs[4].set_ylabel("Power (arb. units)")
    
    axs[5].plot(abs(X_agg[5,:]))
    axs[5].set_xlabel("Time sample index")
    fig.text(0.02, 0.5, 'Voltage amplitude (arb. units)', va='center', rotation='vertical')
    plt.show()
    
    fig, axs = plt.subplots(6)
    axs[0].plot(abs(Vis[0,0]))
    axs[0].set_title("Cross-correlations")
    
    axs[1].plot(abs(Vis[0,1]))
    
    axs[2].plot(abs(Vis[0,2]))
    
    axs[3].plot(abs(Vis[0,3]))
    
    axs[4].plot(abs(Vis[0,4]))
    
    axs[5].plot(abs(Vis[1,2]))
    
    plt.xlabel("Time sample index")
    fig.text(0.02, 0.5, 'Power (arb. units', va='center', rotation='vertical')
    plt.show()
    
    az_theta = np.linspace(0,2*np.pi, deg_range)
    rfi_radius = 1000
    array_radius = 700
    axis_limit = 1200
    plt.figure()
    plt.plot(est_x_range_tdoa*np.cos(est_az_angle_tdoa*np.pi/180),est_y_range_tdoa*np.sin(est_az_angle_tdoa*np.pi/180), 'ro', label='TDOA - x='+str(np.round(est_x_range_tdoa))+', y='+str(np.round(est_y_range_tdoa))+', az='+str(round(est_az_angle_tdoa))+'$^\circ$')
    
    plt.text(rfi_radius*np.cos(est_az_angle_tdoa*np.pi/180),rfi_radius*np.sin(est_az_angle_tdoa*np.pi/180), str(round(est_az_angle_tdoa))+'$^\circ$', horizontalalignment='right')
    plt.text(rfi_radius, 0, '0$^\circ$')
    plt.plot(array_radius*np.cos(az_theta),array_radius*np.sin(az_theta), 'g--')
    plt.plot(rx, ry, 'g1')
    plt.xlim(-1*axis_limit,axis_limit)
    plt.ylim(-1*axis_limit,axis_limit)
    plt.title("TDOA estimate along the horizon of array at " + str(narrowband_freqs[chan_idx[0]][0]/1e6) + " MHz")
    plt.xlabel("Antenna Positions East to West")
    plt.ylabel("Antenna Positions North to South")
    plt.yticks([])
    plt.xticks([])
    #plt.legend(bbox_to_anchor=(1.04,0.5),loc='center left') # Outside of plot
    plt.legend(loc='upper right')
    plt.show()

    end_time = time.time()
    execution_time = end_time-start_time
    print("Execution time = " + str(execution_time) + " seconds")
    print("Done!")


if __name__ == "__main__":
    main()





