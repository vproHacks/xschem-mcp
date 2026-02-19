v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
B 2 100 400 600 580 {flags=graph


divx=5
divy=5
subdivx=4
subdivy=4
xlabmag=1.0
ylabmag=1.0
rawfile=$netlist_dir/rc_circuit.raw
sim_type=tran
x1=5e-07

color=5
node=net2
logx=0
logy=0
x2=0.005
hilight_wave=0}
N 100 170 300 170 {}
N 300 200 300 230 {}
N 300 200 500 200 {}
N 500 170 500 200 {}
N 100 230 100 250 {}
N 500 230 500 250 {}
N 100 250 500 250 {}
N 400 250 400 320 {}
C {vsource.sym} 100 200 0 0 {name=V1 value=3 savecurrent=false}
C {res.sym} 300 200 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 500 200 0 0 {name=C1
m=1
value=1u
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 400 320 0 0 {name=l1 lab=0}
C {simulator_commands.sym} 700 200 0 0 {name=TRAN value=".tran 100u 5m uic"}
