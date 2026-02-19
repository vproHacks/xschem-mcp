v {xschem version=3.4.6 file_version=1.2
*
* Simple RC step response (time constant demo)
}
G {}
K {}
V {}
S {}
E {}

* wiring
N 180 -220 180 -180 {lab=IN}
N 180 -120 180 -90 {lab=0}
N 180 -220 260 -220 {lab=IN}
N 320 -220 430 -220 {lab=OUT}
N 430 -220 430 -160 {lab=OUT}
N 430 -100 430 -90 {lab=0}
N 180 -90 430 -90 {lab=0}

* plot (V(out) vs time)
B 2 560 -420 1360 -120 {flags=graph
y1=-0.1
y2=1.1
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=0.05
divx=5
subdivx=1
node="out"
color=4
dataset=-1
unitx=1
logx=0
logy=0
}

* title / controls / wave loader
C {title.sym} 220 -20 0 0 {name=l1 author="xschem-mcp"}
C {code_shown.sym} 20 -420 0 0 {name=STIMULI
only_toplevel=true
tclcommand="xschem edit_vi_prop"
value="
.control
  save all
  tran 10u 50m uic
  meas tran t63 when v(out)=0.632 rise=1
  write rc_step.raw
.endc
"}
C {launcher.sym} 560 -70 0 0 {name=LOADWAVES
descr=\"load waves\"
tclcommand=\"xschem raw_read $netlist_dir/rc_step.raw tran\"
}

* components
C {vsource.sym} 180 -150 0 0 {name=V1
value=\"pulse 0 1 0 1u 1u 1 2\"
}
C {res.sym} 290 -220 3 0 {name=R1 m=1 value=10k footprint=1206 device=resistor}
C {capa.sym} 430 -130 0 0 {name=C1 m=1 value=1uF footprint=1206 device=\"ceramic capacitor\"}

* labels
C {lab_pin.sym} 180 -220 2 0 {name=lIN sig_type=std_logic lab=IN}
C {lab_pin.sym} 430 -220 2 0 {name=lOUT sig_type=std_logic lab=OUT}
C {lab_pin.sym} 180 -90 2 0 {name=lGND sig_type=std_logic lab=0}

