v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 100 400 600 560 {flags=graph
node="v(out);v(in);-v_dd#branch"
color=4
dataset=0
x1=0
x2=5
divx=5
subdivx=4
logx=0
logy=0
divy=5
subdivy=4
rawfile=$netlist_dir/nmos_cs_amplifier.raw
sim_type=dc}
B 2 100 580 600 740 {flags=graph
node="v(out);v(in)"
color=4
dataset=1
x1=0
x2=2m
divx=5
subdivx=4
logx=0
logy=0
divy=5
subdivy=4
rawfile=$netlist_dir/nmos_cs_amplifier.raw
sim_type=tran}
N 200 50 300 50 {
lab=#net1}
N 300 50 300 110 {
lab=#net1}
N 300 170 420 170 {
lab=out}
N 200 230 380 230 {
lab=in}
N 380 200 380 230 {
lab=in}
N 200 290 200 300 {
lab=0}
N 420 230 420 300 {
lab=0}
N 420 200 420 230 {
lab=0}
N 200 300 300 300 {
lab=0}
N 300 300 420 300 {
lab=0}
N 300 300 300 320 {
lab=0}
N 200 110 200 220 {
lab=0}
N 200 240 200 300 {
lab=0}
N 100 110 200 110 {
lab=0}
N 100 110 100 300 {
lab=0}
N 100 300 200 300 {
lab=0}
C {vsource.sym} 200 80 0 0 {name=V_DD value=5}
C {res.sym} 300 140 0 0 {name=R_D value=2.5k}
C {nmos4.sym} 400 200 0 0 {name=M1 model=ALD1101 w=1738u l=1u}
C {vsource.sym} 200 260 0 0 {name=V_in value=2.5}
C {gnd.sym} 300 320 0 0 {name=GND lab=0}
C {code_shown.sym} 600 100 0 0 {name=MODEL value=".MODEL ALD1101 NMOS LEVEL = 2 UO = 12.72 VTO = 0.6766 NFS = 1.154E12 TOX = 1E-08 NSUB = 3.892E17 UCRIT = 4.582E05 UEXP = 0.07025 VMAX = 6363 RS = 9.491 RD = 5.659 XJ = 4.787E-09 LD = 0 DELTA = 1E-12 NEFF = 0.8345 NSS = -3.801 CGSO = 1.15E-9 CGDO = 1.15E-9 CGBO = 0 CBD = 0 CBS = 0 CJ = 0 MJ = 0.5  CJSW = 0 MJSW = 0.6057 IS = 1.0E-14 PB = 0.8 FC = 0.5 NEFF=5"}
C {simulator_commands.sym} 600 200 0 0 {name=DC value=".dc V_in 0 5 0.01"}
C {simulator_commands.sym} 600 280 0 0 {name=TRAN value=".tran 10u 2m"}
C {lab_pin.sym} 360 170 0 0 {name=lout lab=out}
C {lab_pin.sym} 280 230 0 0 {name=lin lab=in}
