import matplotlib.pyplot as plt
import numpy as np
import mousedata_add,  ImportData
import Cal, CFD, zero_phase_filter

# MAIN
if __name__ == "__main__":
    # Constant
    SamplingTime = 0.001
    CPI = 1600
    ## 木盤半徑12.5 壓克力盤半徑12.53
    wood = 12.5
    plastic = 11.14 # 12.53
    r = plastic
    ## 讀取檔案
    path1 = ['C:/Users/vscla\Desktop\ASUS\cmake_mouse_boundary_v8_1/build\IPS500_G20_motion.txt'] #馬達資料.txt路徑
    path2 = ['C:/Users/vscla\Desktop\ASUS\cmake_mouse_boundary_v8_1/build\IPS500_G20_mouse.txt']  #滑鼠資料.txt路徑
    # path1 = ['D:\ASUS_program_code\控制台增強\WIRELESS\WIRELESS/1600/force\IPS500_G10_motion_1.txt'] #馬達資料.txt路徑
    # path2 = ['D:\ASUS_program_code\控制台增強\WIRELESS\WIRELESS/1600/force\IPS500_G10_mouse_1.txt']  #滑鼠資料.txt路徑
    Motordata, Mousedata = ImportData.ImportData(path1, path2)
    mouseX, mouseY, Pos, PosCmd, Vel, VelCmd, TorCtrl, mousedata_data, mouse_displacement, mouse_real_Pos = Cal.Cal(Mousedata, Motordata, SamplingTime, CPI)    
    t = np.arange(0, (len(Motordata[:,0])) * SamplingTime, SamplingTime)
    # 將資料濾波
    filtered_Pos = zero_phase_filter.zero_phase_filter(3, 17, Pos)
    filtered_PosCmd = zero_phase_filter.zero_phase_filter(3, 50, PosCmd)
    filtered_mouse_real_Pos = zero_phase_filter.zero_phase_filter(3, 14, mouse_real_Pos)
    Pos = filtered_Pos
    PosCmd = filtered_PosCmd
    mouse_real_Pos = filtered_mouse_real_Pos

    ## CFD 速度&加速度
    Pos_CFD_est, Vel_CFD_est, Acc_CFD_est = CFD.CFD(Pos) #濾波
    Pos_CFD_Cmd, Vel_CFD_Cmd, Acc_CFD_Cmd = CFD.CFD(PosCmd) #濾波
    Pos_CFD_est_mouse, Vel_CFD_est_mouse, Acc_CFD_est_mouse = CFD.CFD(mouse_real_Pos) #濾波

    # Plot Pos&PosCmd
    plt.figure(1)
    plt.plot(t, Pos, label='Pos')
    plt.plot(t, PosCmd, label='PosCmd')
    plt.title("Pos")
    plt.legend()
    plt.xlabel("Time(sec)")
    plt.ylabel("rad")

    # Plot Poserr
    plt.figure(2)
    plt.plot(t, PosCmd - Pos)
    plt.title("Poserr")

    # Plot Vel and VelCmd
    plt.figure(3)
    plt.plot(t, Vel, label='Vel')
    plt.plot(t, VelCmd, label='VelCmd')
    plt.title("Vel")
    plt.legend()
    plt.xlabel("Time(sec)")
    plt.ylabel("rad/s")

    # Plot Velerr
    plt.figure(4)
    plt.plot(t, VelCmd - Vel)
    plt.title("Velerr")

    # Plot TorCtrl
    plt.figure(5)
    plt.plot(t, TorCtrl)
    plt.title("TorCtrl")

    # Plot mousex
    plt.figure(6)
    plt.plot(mousedata_data[:,2], mouseX/CPI)
    plt.title("mousex")
    plt.xlabel("Time(sec)")
    plt.ylabel("in")

    # Plot mousey
    plt.figure(7)
    plt.plot(mousedata_data[:,2], mouseY/CPI)
    plt.title("mousey")
    plt.xlabel("Time(sec)")
    plt.ylabel("in")

    # Plot mousex^2+mousey^2
    plt.figure(8)
    plt.plot(mousedata_data[:,2], np.sqrt(mouseX**2 + mouseY**2)/CPI)
    plt.title("mousex^2+mousey^2")
    plt.xlabel("Time(sec)")
    plt.ylabel("in")

    # Plot mouse path
    plt.figure(10)
    plt.plot(mouseX/CPI, mouseY/CPI)
    slope = (mouseY[len(Mousedata)-1]-mouseY[0])/(mouseX[len(Mousedata)-1]-mouseX[0])
    plt.text(3, 8, slope, fontsize=12, color='blue')
    plt.title("Mouse Path")
    plt.xlabel("Mouse X Displacement (in)")
    plt.ylabel("Mouse Y Displacement (in)")

    # 位移比较图
    plt.figure(11)
    plt.plot(t, Pos_CFD_est, label="Filtered Motor Displacement")
    plt.title("Filtered Motor and Mouse Displacement Comparison")
    plt.xlabel("Time (sec)")
    plt.ylabel("Motor Displacement (rad)")
    plt.axis([0, t[-1], min(Pos_CFD_est), max(Pos_CFD_est)])
    handles1, labels1 = plt.gca().get_legend_handles_labels()
    plt.twinx()
    plt.plot(t, Pos_CFD_est_mouse, 'r', label="Filtered Mouse Displacement")
    plt.ylabel("Mouse Displacement (pixel)")
    handles2, labels2 = plt.gca().get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    plt.legend(handles, labels, loc="lower center")

    # 速度比较图
    plt.figure()
    Vel_CFD_est = [x*r/2.54 for x in Vel_CFD_est] 
    Vel_CFD_est_mouse_real = Vel_CFD_est_mouse
    plt.plot(t, Vel_CFD_est, label="Filtered CFD Estimator Motor Velocity")
    plt.title("Filtered CFD Estimator Motor and Mouse Velocity Comparison")
    plt.xlabel("Time (sec)")
    plt.ylabel("Motor Velocity (IPS)")
    plt.axis([0, t[-1], 0, max(max(Vel_CFD_est),max(Vel_CFD_est_mouse))+50])
    handles1, labels1 = plt.gca().get_legend_handles_labels()
    plt.twinx()
    plt.plot(t, Vel_CFD_est_mouse_real, 'r', label="Filtered CFD Estimator Mouse Velocity")
    plt.ylabel("Mouse Velocity (IPS)")
    plt.axis([0, t[-1], 0, max(max(Vel_CFD_est),max(Vel_CFD_est_mouse))+50])
    handles2, labels2 = plt.gca().get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    plt.legend(handles, labels, loc="lower center")

    # 加速度比较图
    plt.figure()
    Acc_CFD_est = [x*r*0.01/9.81 for x in Acc_CFD_est]
    Acc_CFD_est_mouse = [x*0.0254/ 9.81 for x in Acc_CFD_est_mouse]
    Acc_CFD_est_mouse_real = Acc_CFD_est_mouse 
    plt.plot(t, Acc_CFD_est, label="Filtered CFD Estimator Motor Acceleration")
    plt.title("Filtered CFD Estimator Motor and Mouse Acceleration Comparison")
    plt.xlabel("Time (sec)")
    plt.ylabel("Motor Acceleration (G)")
    plt.axis([0, t[-1], min(min(Acc_CFD_est),min(Acc_CFD_est_mouse_real))-5, max(max(Acc_CFD_est),max(Acc_CFD_est_mouse_real))+5])
    handles1, labels1 = plt.gca().get_legend_handles_labels()
    plt.twinx()
    plt.plot(t, Acc_CFD_est_mouse_real, 'r', label="Filtered CFD Estimator Mouse Acceleration")
    plt.ylabel("Mouse Acceleration (G)")
    plt.axis([0, t[-1], min(min(Acc_CFD_est),min(Acc_CFD_est_mouse_real))-5, max(max(Acc_CFD_est),max(Acc_CFD_est_mouse_real))+5])
    handles2, labels2 = plt.gca().get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    plt.legend(handles, labels, loc="lower center")

    # 速度误差
    plt.figure(14)
    deviation = np.abs(Vel_CFD_est_mouse - Vel_CFD_est) / np.where(Vel_CFD_est != 0, Vel_CFD_est, 1) * 100
    plt.plot(t, deviation)
    plt.title("Filtered Velocity Error")
    plt.xlabel("Time (sec)")
    plt.ylabel("Error (%)")
    # plt.axis([0, t[-1], 0, max(deviation)+5])

    plt.show()
