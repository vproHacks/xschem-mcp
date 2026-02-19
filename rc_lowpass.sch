v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 100 170 300 170 {}
N 300 200 300 230 {}
N 300 200 500 200 {}
N 500 170 500 200 {}
N 100 230 100 250 {}
N 500 230 500 250 {}
N 100 250 500 250 {}
N 400 250 400 320 {}
C {vsource.sym} 100 200 0 0 {name=V1 value="AC 1 PULSE(0 1 0 1n 1n 10u 20u)" savecurrent=false}
C {res.sym} 300 200 0 0 {name=R1 value=1k}
C {capa.sym} 500 200 0 0 {name=C1 value=1n}
C {gnd.sym} 400 320 0 0 {name=l1 lab=0}
C {simulator_commands.sym} 700 100 0 0 {name=AC value=".ac dec 50 100 100meg"}
C {simulator_commands.sym} 700 200 0 0 {name=TRAN value=".tran 100n 25u uic"}
C {lab_pin.sym} 400 200 0 0 {name=lout lab=out}

B 2 100 400 600 560 {flags=graph
node="out"
color=4
dataset=-1
x1=100
x2=100meg
divx=5
subdivx=5
logx=1
logy=0
divy=5
subdivy=1
rawfile=$netlist_dir/rc_lowpass.raw
sim_type=ac}

B 2 100 580 600 740 {flags=graph
node="out"
color=4
dataset=-1
x1=0
x2=25u
divx=5
subdivx=1
logx=0
logy=0
divy=5
subdivy=1
rawfile=$netlist_dir/rc_lowpass.raw
sim_type=tran}
