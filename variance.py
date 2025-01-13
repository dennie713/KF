import numpy as np
import mousedata_add
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np
import sys
import mousedata_add,  ImportData
import Cal, CFD, KF_v2, zero_phase_filter

path1 = ['Raw_Data/IPS650_G50_F_motion.txt'] #馬達資料.txt路徑
path2 = ['Raw_Data/IPS650_G50_F_mouse.txt']  #滑鼠資料.txt路徑
# path1 = ['D:\ASUS_program_code\zero_tor\IPS650_G50_motion.txt'] #馬達資料.txt路徑
# path2 = ['D:\ASUS_program_code\zero_tor\IPS650_G50_mouse.txt']  #滑鼠資料.txt路徑
# path1 = ['D:\ASUS_program_code\控制台增強\WIRELESS\WIRELESS/1600/force\IPS500_G10_motion_1.txt'] #馬達資料.txt路徑
# path2 = ['D:\ASUS_program_code\控制台增強\WIRELESS\WIRELESS/1600/force\IPS500_G10_mouse_1.txt']  #滑鼠資料.txt路徑
CPI = 1600
SamplingTime = 0.001
for i in range (len(path1)):
    #Motordata
    Motordata = []
    with open(path1[i], 'r')as f:
        lines = f.readlines()
        for line in lines:
            line = line.split()
            Motordata.append(line) #馬達資料

    #Mousedata
    Mousedata = []
    with open(path2[i], 'r')as f:
        lines = f.readlines()
        for line in lines:
            line = line.split()
            Mousedata.append(line) #滑鼠資料

# #Motordata ,Mousedata    
Motordata = np.array(Motordata)    
Mousedata = np.array(Mousedata)
Pos = np.array(Motordata[:, 3],float)
PosCmd = np.array(Motordata[:, 4],float)
Vel = np.array(Motordata[:, 5],float)
VelCmd = np.array(Motordata[:, 6],float)
AccCmd = np.array(Motordata[:, 8],float)
# Processing mouse data
mousedata_data = mousedata_add.mousedata_add(Mousedata, Mousedata)
mouseX = np.array(abs(mousedata_data[:, 0]),float)
mouseY = np.array(mousedata_data[:, 1],float)
mouse_displacement = mousedata_data[:, 5].astype(float)
t = np.arange(0, (len(Motordata[:,0])) * SamplingTime, SamplingTime)
# Interpolating mouse displacement
mouse_real_Pos = interp1d(np.array(mousedata_data[:, 2],float), mouse_displacement, fill_value="extrapolate")(t) / CPI #得到inch
mouse_in2rad = mouse_real_Pos*2.54/12.5 #inch to rad

Pos_CFD_est, Vel_CFD_est, Acc_CFD_est = CFD.CFD(Pos) 
Pos_CFD_Cmd, Vel_CFD_Cmd, Acc_CFD_Cmd = CFD.CFD(PosCmd) 
Pos_CFD_est_mouse, Vel_CFD_est_mouse, Acc_CFD_est_mouse = CFD.CFD(mouse_real_Pos) 

zk = []
err = []
Acc_CFD_est
for i in range(len(Pos)-1):
    dt = 0.001
    zk = np.array([[Pos[i]], 
                    [Vel[i]],
                    [Acc_CFD_est[i]]]) # vel為LSF1/4
    zk_1 = np.array([[Pos[i+1]], 
                    [Vel[i+1]],
                    [Acc_CFD_est[i+1]]]) # vel為LSF1/4
    A = np.array([[1, dt, 0.5*dt**2],
                  [0, 1, dt],
                  [0, 0, 1 ]])
    error = zk_1 - A @ zk
    err.append(error)
err = np.array(err).squeeze()
print(err)
print("np.cov(err) = ", np.cov(err.T)) 
print("zk = ", zk)
print("zk_1 = ", zk_1)
print("A*zk = ", A @ zk)
print("error = ", error)
variance_p = np.var(err[:, 0])
print("variance_p = ", variance_p)
variance_v = np.var(err[:, 1])
print("variance_v = ", variance_v)
variance_a = np.var(err[:, 2])
print("variance_a = ", variance_a)



# print(PosCmd)
# print(VelCmd)
# 计算变异散度
dev1 = np.array(Pos) - np.array(PosCmd)
# print(dev1)
ave_dev1 = np.mean(dev1)
# print("ave_dev1:", ave_dev1)
# print("max_dev1", max(dev1))
# print("min_dev1", min(dev1))
variance1 = np.var(dev1)
# print("Variance:", variance1)

dev2 = np.array(Vel) - np.array(VelCmd)
variance2 = np.var(dev2)
# print("Variance:", variance2)
# print("AccCmd Variance:",np.var(AccCmd))
# print("VelCmd Variance:",np.var(VelCmd))
dev3 = np.array(Acc_CFD_est) - np.array(AccCmd)
variance3 = np.var(dev3)
print("Pos Variance:",variance1)
print("Vel Variance:",variance2)
print("acc Variance:",variance3)

# print('cov =', np.cov())
# 變藝術
#PosCmd = 5501 , Pos = 5501
#VelCmd = 289 , Vel = 277
print('-------------------------------------------------------------')

#--------------------------------------------------sim data processing------------------------------------------------#
path1 = ['sim_data/raw_data_all_2000.txt'] #馬達資料.txt路徑
SamplingTime = 0.001
for i in range (len(path1)):
    #Simdata
    Simdata = []
    with open(path1[i], 'r')as f:
        lines = f.readlines()
        for line in lines:
            line = line.split()
            Simdata.append(line) #模擬資料

Simdata = np.array(Simdata, dtype=np.float64)
pos_data = Simdata[:, 0]
vel_data = Simdata[:, 1]
acc_data = Simdata[:, 2]

zk = []
err = []
Acc_CFD_est
for i in range(len(pos_data)-1):
    dt = 0.001
    zk = np.array([[pos_data[i]], 
                    [vel_data[i]],
                    [acc_data[i]]]) # vel為LSF1/4
    zk_1 = np.array([[pos_data[i+1]], 
                    [vel_data[i+1]],
                    [acc_data[i+1]]]) # vel為LSF1/4
    A = np.array([[1, dt, 0.5*dt**2],
                  [0, 1, dt],
                  [0, 0, 1 ]])
    # print("zk = ", zk)
    # print("zk_1 = ", zk_1)
    # print("A =", A)
    # print("A*zk = ", A @ zk)
    error = zk_1 - A @ zk
    err.append(error)
err = np.array(err).squeeze()
# print(err)
print("np.cov(err) = \n", np.cov(err.T)) 
# print("zk = ", zk)
# print("zk_1 = ", zk_1)
# print("A*zk = ", A @ zk)
# print("error = ", error)
variance_p = np.var(err[:, 0])
print("variance_p = ", variance_p)
variance_v = np.var(err[:, 1])
print("variance_v = ", variance_v)
variance_a = np.var(err[:, 2])
print("variance_a = ", variance_a)