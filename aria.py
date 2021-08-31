#!/usr/bin/env python3

import sys
import csv
import time
import matplotlib.pyplot as plt
from logger import Logger
from ADS1115 import ADS1115
from SDS011 import SDS011


if __name__ == '__main__':

    dataname = time.strftime('%d_%m_%Y_%H_%M_%S') # current date and time to name the files
    sys.stdout = Logger() # to both show stdout in the console and also save it in a log file
    
    print('ARIA data acquisition')
    print('Serial numbers:')
    print('NO2: 212890332')
    print('CO: 132420228')
    
    val = input('Type y to confirm serial numbers match: ')
    if val != 'y':
        exit("Wrong sensors")

    # values for sensor NO2 serial number 212890332
    WE_e_NO2 = 300
    AE_e_NO2 = 305
    sens_NO2 = 0.218
    n_NO2    = 1.9

    # values for sensor CO serial number 132420228
    WE_e_CO = 272
    AE_e_CO = 258
    sens_CO = 0.252
    n_CO    = -1.5
    
    print('Sensors init')
    part_sensor = SDS011('/dev/ttyUSB0')
    gas_sensor = ADS1115()
    
    print('Read single sample')
    pm25, pm10, time = part_sensor.get_data()
    gas = gas_sensor.get_data() 
    print(pm25, pm10, gas[0], gas[1], gas[2], gas[3]) # gas[0] = WE_NO2, gas[1] = AE_NO2, gas[2] = WE_CO, gas[3] = AE_CO
    
    print('Init plotting')
    plt.ion()
    fig, ax = plt.subplots(5,1)

    # initialize data structures for plots
    BUFF_LEN = 60 # dimension of the buffer which holds the sensor data
    x  = y0 = y1 = y2 = y3 = y4 = y5 = ([] for i in range(6))
    l0 = l1 = l2 = l3 = l4 = l5 = None
    
    n = 0 # iteration counter

    write_file_headers() # Write headers of the raw and processed output files

    print('Enter acquisition loop')

    # Start time count
    start_time = time.time()
    
    while True:
        
        time_elapsed = time.time() - start_time

        print("Time elapsed: " + str(time_elapsed))
        
        # get data from sensors
        pm25, pm10, time = part_sensor.get_data()
        gas = gas_sensor.get_data()
        
        print("pm25     pm10     WE_NO2    AE_NO2      WE_CO     AE_CO") 
        
        print("%5.3f   %5.3f   %5.3f   %5.3f   %5.3f   %5.3f" % (pm25, pm10, gas[0], gas[1], gas[2], gas[3]), "    valori misurati")

        # Write raw data to txt
        txtraw = open('/home/pi/Desktop/Refactor/rilevazioni/misuredrone' + dataname + '.txt','a')
        txtraw.write('%r %r %r %r %r %r %r %r %r \n' % (time_elapsed, pm25, pm10, gas[0], gas[1], gas[2], gas[3], time.strftime('%d/%m/%Y'), time.strftime('%H:%M:%S')))
        txtraw.close()

        # Write raw data to csv
        csvraw = open('/home/pi/Desktop/Refactor/rilevazioni/misuredrone' + dataname + '.csv','a', newline = '')
        csvraw_writer = csv.writer(csvraw, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvraw_writer.writerow([time_elapsed, pm25, pm10, gas[0], gas[1], gas[2], gas[3], time.strftime('%d/%m/%Y'), time.strftime('%H:%M:%S')])
        csvraw.close()

        # Here convert raw ADC data to eng. values
        # from ug/m3 to ppb      

        gaspic = [0,0,0,0];
        gaspic[0] = (((gas[0] - WE_e_NO2) - (n_NO2 * (gas[1] - AE_e_NO2))) / (sens_NO2))   # NO2 sensor
        gaspic[1] = (((gas[2] - WE_e_CO)-( n_CO*(gas[3] - AE_e_CO)))/ (sens_CO))    # CO sensor
        gaspic[2] = 0.0     # (gas[2] - 260)/ 0.369     # NO2 sensor
        gaspic[3] = 0.0     # gas[3]*4.1569 - 1269.6     # PID    ( VOCs )
        
        print("pm25     pm10     NO2      CO       NO   VOCs") 
        print("%5.3f   %5.3f   %5.3f   %5.3f   %5.3f   %5.3f" % (pm25, pm10, gaspic[0], gaspic[1], gaspic[2], gaspic[3]),"    valori grafico  (ppb)  (pm in ug/m^3 e VOCs in mV)")
        
        # convert from ppb to ug/m^3
        gasmicro = [0,0,0,0];
        gasmicro[0]= gaspic[0] * 1.88 #NO2
        gasmicro[1]= gaspic[1] * 1.145 #CO
        gasmicro[2]= gaspic[2] * 1.45 #NO (== 0)
        gasmicro[3]= gaspic[3] #VOCs (== 0)

        # Write processed data to txt
        print("%5.3f   %5.3f   %5.3f   %5.3f   %5.3f   %5.3f" % (pm25, pm10, gas[0], gas[1], gas[2], gas[3]), "    valori misurati")
        txtProc = open('/home/pi/Desktop/Refactor/rilevazioni/misuredroneProc' + dataname + '.txt','a')
        txtProc.write('%r %r %r %r %r %r %r %r %r \n' % (time_elapsed, pm25, pm10, gasmicro[0], gasmicro[1], gasmicro[2], gasmicro[3], time.strftime('%d/%m/%Y'), time.strftime('%H:%M:%S')))
        txtProc.close()

        # Write processed data to csv
        csvProc = open('/home/pi/Desktop/Refactor/rilevazioni/misuredroneProc' + dataname + '.csv','a', newline = '')
        csvProc_writer = csv.writer(csvProc, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvProc_writer.writerow([time_elapsed, pm25, pm10, gasmicro[0], gasmicro[1], gasmicro[2], gasmicro[3], time.strftime('%d/%m/%Y'), time.strftime('%H:%M:%S')])
        csvProc.close()

        print("%5.3f   %5.3f   %5.3f   %5.3f   %5.3f   %5.3f" % (pm25, pm10, gasmicro[0], gasmicro[1], gasmicro[2], gasmicro[3]),"    valori grafico  (migrogrammi/m^3)  (pm in ug/m^3 e VOCs in mV)")  
        
        print("\n")

        # Plot in console
        # Store into the queues
        x.append(time_elapsed)
        y0.append(pm25)
        y1.append(pm10)
        y2.append(gasmicro[0]) #NO2
        y3.append(gasmicro[1]) #CO
        y4.append(gaspic[2]) #NO
        y5.append(gaspic[3]) #VOCs
        if len(x) > BUFF_LEN: # keep only the latest 60 elements
            x = x[-BUFF_LEN:]
            y0 = y0[-BUFF_LEN:]
            y1 = y1[-BUFF_LEN:]
            y2 = y2[-BUFF_LEN:]
            y3 = y3[-BUFF_LEN:]
            y4 = y4[-BUFF_LEN:]
            y5 = y5[-BUFF_LEN:]

        # Plot
        if n == 0:
            l0, = ax[0].plot(x, y0,'-*', alpha=0.8)    # pm2.5
            l1, = ax[0].plot(x, y1, 'y-s', alpha=0.8)  # pm10
            l2, = ax[1].plot(x, y2, 'r-o', alpha=0.8)  # NO2
            l3, = ax[2].plot(x, y3, 'g-o', alpha=0.8)  # CO
            l4, = ax[3].plot(x, y4, 'c-*', alpha=0.8)  # NO
            l5, = ax[4].plot(x, y5, 'k-*', alpha=0.8)  # VOCs
        else:
            l0.set_data(x, y0)
            ax[0].relim()
            ax[0].autoscale_view()
            ax[0].set_ylabel('pm [ug]')
            l1.set_data(x, y1)
            ax[0].relim()
            ax[0].autoscale_view()
            ax[0].legend(( l0, l1),('pm 2.5','pm 10'))
            l2.set_data(x, y2)
            ax[1].relim()
            ax[1].autoscale_view()
            ax[1].set_ylabel(' NO2 [ug/m3] ')
            l3.set_data(x, y3)
            ax[2].relim()
            ax[2].autoscale_view()
            ax[2].set_ylabel(' CO [ug/m3] ')
            l4.set_data(x, y4)
            ax[3].relim()
            ax[3].autoscale_view()
            ax[3].set_ylabel(' NO [ppb] ')
            l5.set_data(x, y5)
            ax[4].relim()
            ax[4].autoscale_view()
            ax[4].set_ylabel(' VOCs [mV] ')

        n = n + 1
        
        plt.draw()
        plt.xlabel('time s')
        
        plt.pause(1.0)

        # Wait 1 sec before acquiring next data point
        time.sleep(1.0)


        # Utility function to write headers of the output files
        def write_file_headers():
            # print raw files headers
            # txt file
            txtraw = open('/home/pi/Desktop/Refactor/rilevazioni/misuredrone' + dataname + '.txt','w')
            txtraw.write('%r %r %r %r %r %r %r %r %r \n' % ('time_elapsed', 'pm25 [ug]/m3', 'pm10 [ug]/m3', 'WE_NO2  [mV] ', 'AE_NO2  [mV] ', 'WE_CO  [mV] ', 'AE_CO [mV]', 'data', 'ora'))
            txtraw.close()
            # csv file
            csvraw = open('/home/pi/Desktop/Refactor/rilevazioni/misuredrone' + dataname + '.csv','w', newline = '')
            csvraw_writer = csv.writer(csvraw, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvraw_writer.writerow(['time_elapsed', 'pm25 [ug]/m3', 'pm10 [ug]/m3', 'WE_NO2  [mV] ', 'AE_NO2  [mV] ', 'WE_CO  [mV] ', 'AE_CO [mV]', 'data', 'ora'])
            csvraw.close()
            
            # print processed files headers
            # txt file
            txtProc = open('/home/pi/Desktop/Refactor/rilevazioni/misuredroneProc' + dataname + '.txt','w')
            txtProc.write('%r %r %r %r %r %r %r %r %r \n' % ('time_elapsed', 'pm25 [ug]/m3', 'pm10 [ug]/m3', 'NO2  [ug/m3] ', 'CO  [ug/m3] ', '/', '/', 'data', 'ora'))
            txtProc.close()
            # csv file
            csvProc = open('/home/pi/Desktop/Refactor/rilevazioni/misuredroneProc' + dataname + '.csv','w', newline = '')
            csvProc_writer = csv.writer(csvProc, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvProc_writer.writerow(['time_elapsed', 'pm25 [ug]/m3', 'pm10 [ug]/m3', 'NO2  [ug/m3] ', 'CO  [ug/m3] ', '/', '/', 'data', 'ora'])
            csvProc.close()