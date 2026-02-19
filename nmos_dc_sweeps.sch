v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 100 400 600 560 {flags=graph
node="\\"i(vd) -1 *\\""
color=4
dataset=0
x1=0
x2=3
divx=5
subdivx=4
logx=0
logy=0
divy=5
subdivy=4
rawfile=$netlist_dir/nmos_dc_sweeps.raw
sim_type=dc
y1=-5.1e-05
y2=1.5e-11
}
B 2 100 577.5 600 737.5 {flags=graph
node="\\"i(vd) -1 *\\""
color=4
dataset=1
x1=0
x2=3
divx=5
subdivx=1
logx=0
logy=0
divy=5
subdivy=1
rawfile=$netlist_dir/nmos_dc_sweeps.raw
sim_type=dc

y2=1.9e-11

y1=-2.7e-23
rainbow=0}
N 200 110 380 200 {
lab=G}
N 200 290 200 300 {
lab=0}
N 420 230 420 300 {
lab=0}
N 200 300 420 300 {
lab=0}
N 300 300 300 320 {
lab=0}
N 200 170 200 220 {
lab=#net1}
N 200 240 200 300 {
lab=0}
N 200 230 310 230 {
lab=D}
N 310 170 310 230 {
lab=D}
N 310 170 420 170 {
lab=D}
C {nmos4.sym} 400 200 0 0 {name=M1 model=ALD1101 w=1738u l=1u del=0 m=1}
C {vsource.sym} 200 140 0 0 {name=VG value=1}
C {vsource.sym} 200 260 0 0 {name=VD value=1}
C {gnd.sym} 300 320 0 0 {name=l1 lab=0}
C {code_shown.sym} 600 100 0 0 {name=MODEL value=".MODEL ALD1101 NMOS LEVEL = 2 UO = 12.72 VTO = 0.6766 NFS = 1.154E12 TOX = 1E-08 NSUB = 3.892E17 UCRIT = 4.582E05 UEXP = 0.07025 VMAX = 6363 RS = 9.491 RD = 5.659 XJ = 4.787E-09 LD = 0 DELTA = 1E-12 NEFF = 0.8345 NSS = -3.801 CGSO = 1.15E-9 CGDO = 1.15E-9 CGBO = 0 CBD = 0 CBS = 0 CJ = 0 MJ = 0.5  CJSW = 0 MJSW = 0.6057 IS = 1.0E-14 PB = 0.8 FC = 0.5 NEFF=5"}
C {simulator_commands.sym} 600 200 0 0 {name=DC_VD value=".dc VD 0 3 0.01"}
C {simulator_commands.sym} 600 280 0 0 {name=DC_VG value=".dc VG 0 3 0.01"}
C {lab_pin.sym} 310 200 0 0 {name=lD lab=D}
C {lab_pin.sym} 380 200 0 0 {name=netlabel_M1_g lab=G}
C {lab_pin.sym} 200 110 0 0 {name=netlabel_VG_p lab=G}
C {lab_pin.sym} 420 200 0 0 {name=netlabel_M1_b lab=0}
