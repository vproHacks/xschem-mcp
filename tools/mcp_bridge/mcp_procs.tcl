# MCP wrapper procs for XSchem -- sourced dynamically by the MCP bridge.
# These procs wrap raw `xschem` commands and return normalised JSON payloads.

namespace eval mcp {
  variable api_version 1
  variable supported_netlist_types {spice verilog vhdl spectre tedax}
}

proc mcp::json_escape {s} {
  return [string map [list "\\" "\\\\" "\"" "\\\"" "\n" "\\n" "\r" "\\r" "\t" "\\t"] $s]
}

proc mcp::json_object {kv_list} {
  if {[llength $kv_list] % 2 != 0} {
    error "json_object expects key/value pairs"
  }
  set parts {}
  foreach {k v} $kv_list {
    lappend parts "\"[mcp::json_escape $k]\":\"[mcp::json_escape $v]\""
  }
  return "\{[join $parts ,]\}"
}

proc mcp::result {status code message {kv_list {}}} {
  set now [clock seconds]
  set data_json [mcp::json_object $kv_list]
  return "\{\"status\":\"[mcp::json_escape $status]\",\"code\":\"[mcp::json_escape $code]\",\"message\":\"[mcp::json_escape $message]\",\"timestamp\":\"$now\",\"data\":$data_json\}"
}

proc mcp::ok {{kv_list {}}} {
  return [mcp::result ok ok {} $kv_list]
}

proc mcp::err {code message} {
  return [mcp::result error $code $message]
}

proc mcp::require_numeric {name value} {
  if {![string is double -strict $value]} {
    error "$name must be numeric"
  }
}

proc mcp::default_netlist_file {} {
  global netlist_dir USER_CONF_DIR
  set nd [xschem get netlist_dir]
  if {$nd eq {}} {
    set nd $netlist_dir
  }
  if {$nd eq {}} {
    set nd "$USER_CONF_DIR/simulations"
  }
  regsub {/$} $nd {} nd
  set custom_netlist_name [xschem get netlist_name]
  if {$custom_netlist_name ne {}} {
    set base [file rootname $custom_netlist_name]
  } else {
    set base [file tail [file rootname [xschem get schname]]]
  }
  set netlist_type [xschem get netlist_type]
  if {$netlist_type eq {verilog}} {
    set ext v
  } else {
    set ext $netlist_type
  }
  return "${nd}/${base}.${ext}"
}

proc mcp_get_context {} {
  if {[catch {
    set current_name [xschem get current_name]
    set schname [xschem get schname]
    set current_win_path [xschem get current_win_path]
    set top_path [xschem get top_path]
    set netlist_type [xschem get netlist_type]
    set netlist_dir [xschem get netlist_dir]
    set instances [xschem get instances]
    set symbols [xschem get symbols]
    set selection_count [xschem get lastsel]
    set first_sel [xschem get first_sel]
    set bbox_selected [xschem get bbox_selected]
    mcp::ok [list \
      api_version $mcp::api_version \
      current_name $current_name \
      schematic $schname \
      current_window $current_win_path \
      top_window $top_path \
      netlist_type $netlist_type \
      netlist_dir $netlist_dir \
      instances $instances \
      symbols $symbols \
      selection_count $selection_count \
      first_selection $first_sel \
      selected_bbox $bbox_selected]
  } result]} {
    return [mcp::err context_error $result]
  }
  return $result
}

proc mcp_search_symbols {{pattern *}} {
  if {[catch {
    global XSCHEM_LIBRARY_PATH
    set results {}
    foreach dir [split $XSCHEM_LIBRARY_PATH :] {
      if {![file isdirectory $dir]} continue
      set lib_name [file tail $dir]
      foreach f [glob -nocomplain -directory $dir ${pattern}.sym] {
        set sym_name [file tail $f]
        lappend results "${sym_name}|${lib_name}|${f}"
      }
    }
    set results [lsort -unique $results]
    set count [llength $results]
    set formatted {}
    foreach entry $results {
      set parts [split $entry |]
      set sym_name [lindex $parts 0]
      set lib_name [lindex $parts 1]
      set abspath [lindex $parts 2]
      append formatted "${sym_name}  (library: ${lib_name}, path: ${abspath})\n"
    }
    mcp::ok [list pattern $pattern count $count symbols [string trim $formatted]]
  } result]} {
    return [mcp::err search_symbols_error $result]
  }
  return $result
}

proc mcp_list_symbols {{include_derived 0}} {
  if {[catch {
    if {$include_derived} {
      set syms [xschem symbols derived_symbols]
    } else {
      set syms [xschem symbols]
    }
    set lines [split [string trim $syms] "\n"]
    if {[llength $lines] == 1 && [string trim [lindex $lines 0]] eq {}} {
      set count 0
    } else {
      set count [llength $lines]
    }
    mcp::ok [list include_derived $include_derived count $count symbols $syms]
  } result]} {
    return [mcp::err list_symbols_error $result]
  }
  return $result
}

proc mcp_place_symbol {symbol_name x y {rot 0} {flip 0} {inst_props {}} {batch_continues 0}} {
  if {[catch {
    if {[string trim $symbol_name] eq {}} {
      error "symbol_name is required"
    }
    mcp::require_numeric x $x
    mcp::require_numeric y $y
    mcp::require_numeric rot $rot
    mcp::require_numeric flip $flip
    set resolved [abs_sym_path $symbol_name]
    if {![file exists $resolved]} {
      error "symbol not found: '$symbol_name' (resolved to '$resolved'). Use xschem.search_symbols to find valid names."
    }
    set first [expr {$batch_continues ? 1 : 0}]
    if {$inst_props eq {}} {
      xschem instance $symbol_name $x $y $rot $flip
    } else {
      xschem instance $symbol_name $x $y $rot $flip $inst_props $first
    }
    xschem redraw
    mcp::ok [list \
      symbol_name $symbol_name \
      resolved_path $resolved \
      x $x y $y rot $rot flip $flip \
      batch_continues $batch_continues]
  } result]} {
    return [mcp::err place_symbol_error $result]
  }
  return $result
}

proc mcp_create_symbol {name {in {}} {out {}} {inout {}} {overwrite 0}} {
  if {[catch {
    if {[string trim $name] eq {}} {
      error "name is required"
    }
    set symname [file rootname $name].sym
    if {$overwrite && [file exists $symname]} {
      file delete -force $symname
    }
    set rc [create_symbol $name $in $out $inout]
    if {!$rc} {
      error "failed creating symbol: $symname"
    }
    mcp::ok [list \
      symbol_file $symname \
      inputs [join $in { }] \
      outputs [join $out { }] \
      inouts [join $inout { }] \
      overwrite $overwrite]
  } result]} {
    return [mcp::err create_symbol_error $result]
  }
  return $result
}

proc mcp_set_instance_property {instance token value {fast 0}} {
  if {[catch {
    if {[string trim $instance] eq {}} { error "instance is required" }
    if {[string trim $token] eq {}} { error "token is required" }
    if {$fast} {
      xschem setprop -fast instance $instance $token $value
    } else {
      xschem setprop instance $instance $token $value
    }
    mcp::ok [list instance $instance token $token value $value fast $fast]
  } result]} {
    return [mcp::err set_instance_property_error $result]
  }
  return $result
}

proc mcp_wire {x1 y1 x2 y2} {
  if {[catch {
    mcp::require_numeric x1 $x1
    mcp::require_numeric y1 $y1
    mcp::require_numeric x2 $x2
    mcp::require_numeric y2 $y2
    xschem wire $x1 $y1 $x2 $y2
    xschem redraw
    mcp::ok [list x1 $x1 y1 $y1 x2 $x2 y2 $y2]
  } result]} {
    return [mcp::err wire_error $result]
  }
  return $result
}

proc mcp::ensure_netlist_dir {} {
  global netlist_dir USER_CONF_DIR
  set_netlist_dir 0
  if {$netlist_dir eq {}} {
    set netlist_dir "$USER_CONF_DIR/simulations"
  }
  if {![file exists $netlist_dir]} {
    file mkdir $netlist_dir
  }
  return $netlist_dir
}

proc mcp_generate_netlist {{filename {}}} {
  if {[catch {
    mcp::ensure_netlist_dir
    if {$filename eq {}} {
      set erc_messages [xschem netlist -messages]
      set netlist_file [mcp::default_netlist_file]
    } else {
      set erc_messages [xschem netlist -messages $filename]
      set netlist_file $filename
    }
    if {![file exists $netlist_file]} {
      error "netlist was not created at '$netlist_file'; check schematic for errors: $erc_messages"
    }
    set netlist_size [file size $netlist_file]
    mcp::ok [list \
      netlist_file $netlist_file \
      netlist_type [xschem get netlist_type] \
      netlist_dir [mcp::ensure_netlist_dir] \
      netlist_size $netlist_size \
      erc_messages $erc_messages]
  } result]} {
    return [mcp::err generate_netlist_error $result]
  }
  return $result
}

proc mcp_run_simulation {{timeout 60}} {
  if {[catch {
    mcp::ensure_netlist_dir
    set netlist_file [mcp::default_netlist_file]
    if {![file exists $netlist_file]} {
      error "netlist not found at '$netlist_file'. Call xschem.generate_netlist first."
    }
    global netlist_dir
    set raw_file "[file rootname $netlist_file].raw"
    set log_file "[file rootname $netlist_file].log"

    set sim_output {}
    set sim_error {}
    set sim_exit_code -1
    if {[catch {
      set sim_output [exec ngspice -b -r $raw_file $netlist_file 2>@1]
      set sim_exit_code 0
    } sim_error]} {
      set sim_exit_code 1
      set sim_output $sim_error
    }

    # Write log for inspection
    set fd [open $log_file w]
    puts $fd $sim_output
    close $fd

    # Trim output for response (last 100 lines max)
    set lines [split $sim_output "\n"]
    set total_lines [llength $lines]
    if {$total_lines > 100} {
      set truncated [join [lrange $lines end-99 end] "\n"]
      set sim_output "... ($total_lines lines, showing last 100) ...\n$truncated"
    }

    set has_raw [file exists $raw_file]
    if {$sim_exit_code != 0} {
      mcp::result error sim_failed "ngspice exited with errors" [list \
        netlist_file $netlist_file \
        raw_file $raw_file \
        raw_file_exists $has_raw \
        log_file $log_file \
        exit_code $sim_exit_code \
        output $sim_output]
    } else {
      mcp::ok [list \
        netlist_file $netlist_file \
        raw_file $raw_file \
        raw_file_exists $has_raw \
        log_file $log_file \
        exit_code $sim_exit_code \
        output $sim_output]
    }
  } result]} {
    return [mcp::err run_simulation_error $result]
  }
  return $result
}

proc mcp_read_simulation_results {{raw_file {}} {sim_type {}}} {
  if {[catch {
    if {$raw_file eq {}} {
      set raw_file [file rootname [mcp::default_netlist_file]].raw
    }
    if {$sim_type eq {}} {
      xschem raw_read $raw_file
    } else {
      xschem raw_read $raw_file $sim_type
    }
    mcp::ok [list raw_file $raw_file sim_type $sim_type]
  } result]} {
    return [mcp::err read_simulation_results_error $result]
  }
  return $result
}

proc mcp_save_schematic {{filename {}} {type schematic}} {
  if {[catch {
    if {$type ni {schematic symbol}} {
      error "type must be 'schematic' or 'symbol', got '$type'"
    }
    if {$filename eq {}} {
      set current [xschem get schname]
      if {$current eq {} || $current eq {untitled.sch}} {
        error "no filename given and schematic is unnamed; provide a filename"
      }
      xschem save
      set saved_path $current
    } else {
      xschem saveas $filename $type
      set saved_path $filename
    }
    mcp::ok [list saved_path $saved_path type $type]
  } result]} {
    return [mcp::err save_schematic_error $result]
  }
  return $result
}

proc mcp_delete {target {arg1 {}} {arg2 {}} {arg3 {}} {arg4 {}}} {
  if {[catch {
    xschem unselect_all
    switch -- $target {
      instance {
        if {$arg1 eq {}} { error "instance name is required" }
        set found [xschem select instance $arg1]
        if {$found eq {0}} {
          error "instance '$arg1' not found"
        }
        xschem delete
        mcp::ok [list target instance name $arg1]
      }
      wire {
        if {$arg1 eq {}} { error "wire index is required" }
        mcp::require_numeric wire_index $arg1
        set found [xschem select wire [expr {int($arg1)}]]
        if {$found eq {0}} {
          error "wire index $arg1 not found"
        }
        xschem delete
        mcp::ok [list target wire index $arg1]
      }
      area {
        if {$arg1 eq {} || $arg2 eq {} || $arg3 eq {} || $arg4 eq {}} {
          error "area requires x1, y1, x2, y2"
        }
        mcp::require_numeric x1 $arg1
        mcp::require_numeric y1 $arg2
        mcp::require_numeric x2 $arg3
        mcp::require_numeric y2 $arg4
        xschem select_inside $arg1 $arg2 $arg3 $arg4
        xschem delete
        mcp::ok [list target area x1 $arg1 y1 $arg2 x2 $arg3 y2 $arg4]
      }
      all {
        xschem select_all
        xschem delete
        xschem redraw
        mcp::ok [list target all]
      }
      default {
        error "unknown target '$target'; must be instance, wire, area, or all"
      }
    }
  } result]} {
    return [mcp::err delete_error $result]
  }
  return $result
}

proc mcp_reload_schematic {} {
  if {[catch {
    set schname [xschem get schname]
    if {$schname eq {} || $schname eq {untitled.sch}} {
      error "no saved schematic to reload"
    }
    if {![file exists $schname]} {
      error "schematic file not found at '$schname'"
    }
    after idle {xschem reload zoom_full}
    mcp::ok [list schematic $schname]
  } result]} {
    return [mcp::err reload_error $result]
  }
  return $result
}

proc mcp_read_schematic {} {
  if {[catch {
    set schname [xschem get schname]
    if {$schname eq {} || $schname eq {untitled.sch}} {
      error "schematic is unnamed or not saved to disk"
    }
    if {![file exists $schname]} {
      error "schematic file not found at '$schname'"
    }
    set fd [open $schname r]
    set contents [read $fd]
    close $fd
    set line_count [llength [split $contents "\n"]]
    mcp::ok [list schematic $schname line_count $line_count contents $contents]
  } result]} {
    return [mcp::err read_schematic_error $result]
  }
  return $result
}

proc mcp_add_graph {x1 y1 x2 y2 signals {raw_file {}} {sim_type {}}} {
  if {[catch {
    mcp::require_numeric x1 $x1
    mcp::require_numeric y1 $y1
    mcp::require_numeric x2 $x2
    mcp::require_numeric y2 $y2

    if {$raw_file eq {}} {
      set raw_file "[file rootname [mcp::default_netlist_file]].raw"
    }

    set schname [xschem get schname]
    if {$schname eq {} || $schname eq {untitled.sch}} {
      error "schematic must be saved before adding a graph"
    }

    xschem save

    set node_str [join $signals "\n"]
    set n_signals [llength $signals]
    set colors {}
    set palette {4 7 5 6 8 9 10 11 12 13 14 15}
    for {set i 0} {$i < $n_signals} {incr i} {
      lappend colors [lindex $palette [expr {$i % [llength $palette]}]]
    }
    set color_str [join $colors " "]

    set rawfile_attr {}
    if {$raw_file ne {}} {
      set rawfile_attr "\nrawfile=$raw_file"
    }
    set sim_attr {}
    if {$sim_type ne {}} {
      set sim_attr "\nsim_type=$sim_type"
    }

    set graph_line "B 2 $x1 $y1 $x2 $y2 \{flags=graph\nnode=\"$node_str\"\ncolor=\"$color_str\"\ndivx=5\ndivy=5\nsubdivx=1\nsubdivy=1\nxlabmag=1.0\nylabmag=1.0${rawfile_attr}${sim_attr}\}"

    set fd [open $schname r]
    set contents [read $fd]
    close $fd

    append contents "\n$graph_line\n"

    set fd [open $schname w]
    puts -nonewline $fd $contents
    close $fd

    if {$sim_type eq {}} {
      after idle [list xschem reload zoom_full]
      after idle [list xschem raw_read $raw_file]
    } else {
      after idle [list xschem reload zoom_full]
      after idle [list xschem raw_read $raw_file $sim_type]
    }
    after idle {xschem redraw}

    mcp::ok [list \
      schematic $schname \
      raw_file $raw_file \
      signals [join $signals {, }] \
      graph_bounds "${x1},${y1} ${x2},${y2}"]
  } result]} {
    return [mcp::err add_graph_error $result]
  }
  return $result
}

proc mcp_annotate_operating_point {{filename {}}} {
  if {[catch {
    if {$filename eq {}} {
      set filename [file rootname [mcp::default_netlist_file]].raw
    }
    xschem annotate_op $filename
    mcp::ok [list file $filename]
  } result]} {
    return [mcp::err annotate_operating_point_error $result]
  }
  return $result
}

proc mcp_get_instance_pins {instance_name} {
  if {[catch {
    if {[string trim $instance_name] eq {}} {
      error "instance_name is required"
    }
    set pin_names [xschem instance_pins $instance_name]
    if {$pin_names eq {}} {
      error "instance '$instance_name' not found or has no pins"
    }
    set pin_data {}
    foreach pin $pin_names {
      set coord_result [xschem instance_pin_coord $instance_name name $pin]
      set px [lindex $coord_result 1]
      set py [lindex $coord_result 2]
      set net [xschem instance_net $instance_name $pin]
      set dir [xschem getprop instance_pin $instance_name $pin dir]
      append pin_data "${pin} x=${px} y=${py} net=${net} dir=${dir}\n"
    }
    set pin_count [llength $pin_names]
    mcp::ok [list \
      instance $instance_name \
      pin_count $pin_count \
      pins [string trim $pin_data]]
  } result]} {
    return [mcp::err get_instance_pins_error $result]
  }
  return $result
}

proc mcp_check_connectivity {} {
  if {[catch {
    set n_inst [xschem get instances]
    set unconnected {}
    set unconnected_count 0
    for {set i 0} {$i < $n_inst} {incr i} {
      set coord [xschem instance_coord $i]
      set inst_name [lindex $coord 0]
      set pin_names [xschem instance_pins $i]
      foreach pin $pin_names {
        set net [xschem instance_net $i $pin]
        if {$net eq {} || [string match {#net*} $net]} {
          set pc [xschem instance_pin_coord $i name $pin]
          set px [lindex $pc 1]
          set py [lindex $pc 2]
          append unconnected "${inst_name}.${pin} x=${px} y=${py} net=${net}\n"
          incr unconnected_count
        }
      }
    }
    mcp::ensure_netlist_dir
    set erc_messages [xschem netlist -messages]
    set info_text [xschem get infowindow_text]
    mcp::ok [list \
      total_instances $n_inst \
      unconnected_count $unconnected_count \
      unconnected_pins [string trim $unconnected] \
      erc_messages $erc_messages \
      info $info_text]
  } result]} {
    return [mcp::err check_connectivity_error $result]
  }
  return $result
}

proc mcp_get_netlist_preview {{max_lines 500}} {
  if {[catch {
    mcp::ensure_netlist_dir
    set erc_messages [xschem netlist -messages]
    set netlist_file [mcp::default_netlist_file]
    if {![file exists $netlist_file]} {
      error "netlist was not created at '$netlist_file'; check schematic for errors: $erc_messages"
    }
    set fd [open $netlist_file r]
    set contents [read $fd]
    close $fd
    set all_lines [split $contents "\n"]
    set total_lines [llength $all_lines]
    if {$total_lines > $max_lines} {
      set contents [join [lrange $all_lines 0 [expr {$max_lines - 1}]] "\n"]
      append contents "\n... (truncated, showing $max_lines of $total_lines lines) ..."
    }
    mcp::ok [list \
      netlist_file $netlist_file \
      netlist_type [xschem get netlist_type] \
      total_lines $total_lines \
      erc_messages $erc_messages \
      contents $contents]
  } result]} {
    return [mcp::err get_netlist_preview_error $result]
  }
  return $result
}

proc mcp_get_pin_coordinates {instance_name pin_name} {
  if {[catch {
    if {[string trim $instance_name] eq {}} {
      error "instance_name is required"
    }
    if {[string trim $pin_name] eq {}} {
      error "pin_name is required"
    }
    set coord_result [xschem instance_pin_coord $instance_name name $pin_name]
    if {$coord_result eq {}} {
      error "pin '$pin_name' not found on instance '$instance_name'"
    }
    set px [lindex $coord_result 1]
    set py [lindex $coord_result 2]
    set net [xschem instance_net $instance_name $pin_name]
    set dir [xschem getprop instance_pin $instance_name $pin_name dir]
    mcp::ok [list \
      instance $instance_name \
      pin $pin_name \
      x $px \
      y $py \
      net $net \
      dir $dir]
  } result]} {
    return [mcp::err get_pin_coordinates_error $result]
  }
  return $result
}

proc mcp_wire_to_pin {instance_name pin_name x y} {
  if {[catch {
    if {[string trim $instance_name] eq {}} {
      error "instance_name is required"
    }
    if {[string trim $pin_name] eq {}} {
      error "pin_name is required"
    }
    mcp::require_numeric x $x
    mcp::require_numeric y $y
    set coord_result [xschem instance_pin_coord $instance_name name $pin_name]
    if {$coord_result eq {}} {
      error "pin '$pin_name' not found on instance '$instance_name'"
    }
    set pin_x [lindex $coord_result 1]
    set pin_y [lindex $coord_result 2]
    xschem wire $x $y $pin_x $pin_y
    xschem redraw
    mcp::ok [list \
      instance $instance_name \
      pin $pin_name \
      from_x $x \
      from_y $y \
      to_x $pin_x \
      to_y $pin_y]
  } result]} {
    return [mcp::err wire_to_pin_error $result]
  }
  return $result
}

proc mcp_get_wire_net_assignment {} {
  if {[catch {
    set n_wires [xschem get wires]
    set wire_data {}
    for {set i 0} {$i < $n_wires} {incr i} {
      set coords [xschem wire_coord $i]
      set x1 [lindex $coords 0]
      set y1 [lindex $coords 1]
      set x2 [lindex $coords 2]
      set y2 [lindex $coords 3]
      set lab [xschem getprop wire $i lab]
      set prop [xschem getprop wire $i prop_ptr]
      if {$lab eq {}} {
        set lab {(unlabeled)}
      }
      append wire_data "wire\[$i\] (${x1},${y1})-(${x2},${y2}) net=${lab}"
      if {$prop ne {} && $prop ne "lab=$lab"} {
        append wire_data " props={${prop}}"
      }
      append wire_data "\n"
    }
    mcp::ok [list \
      total_wires $n_wires \
      wires [string trim $wire_data]]
  } result]} {
    return [mcp::err get_wire_net_assignment_error $result]
  }
  return $result
}

proc mcp_debug_pin_wire_connection {instance_name pin_name} {
  if {[catch {
    if {[string trim $instance_name] eq {}} {
      error "instance_name is required"
    }
    if {[string trim $pin_name] eq {}} {
      error "pin_name is required"
    }
    set coord_result [xschem instance_pin_coord $instance_name name $pin_name]
    if {$coord_result eq {}} {
      error "pin '$pin_name' not found on instance '$instance_name'"
    }
    set pin_x [lindex $coord_result 1]
    set pin_y [lindex $coord_result 2]
    set net [xschem instance_net $instance_name $pin_name]
    set dir [xschem getprop instance_pin $instance_name $pin_name dir]

    set n_wires [xschem get wires]
    set touching_wires {}
    set near_wires {}
    set touching_count 0
    set near_count 0
    set tolerance 5.0

    for {set i 0} {$i < $n_wires} {incr i} {
      set coords [xschem wire_coord $i]
      set wx1 [lindex $coords 0]
      set wy1 [lindex $coords 1]
      set wx2 [lindex $coords 2]
      set wy2 [lindex $coords 3]
      if {![string is double -strict $wx1] || ![string is double -strict $wy1] ||
          ![string is double -strict $wx2] || ![string is double -strict $wy2]} {
        continue
      }
      set lab [xschem getprop wire $i lab]
      if {$lab eq {}} { set lab {(unlabeled)} }

      set d1 [expr {sqrt(($wx1-$pin_x)*($wx1-$pin_x) + ($wy1-$pin_y)*($wy1-$pin_y))}]
      set d2 [expr {sqrt(($wx2-$pin_x)*($wx2-$pin_x) + ($wy2-$pin_y)*($wy2-$pin_y))}]
      set min_endpoint_dist [expr {min($d1, $d2)}]

      set touches [xschem touch $wx1 $wy1 $wx2 $wy2 $pin_x $pin_y]

      if {$touches || $min_endpoint_dist < 0.1} {
        append touching_wires "wire\[$i\] (${wx1},${wy1})-(${wx2},${wy2}) net=${lab} endpoint_dist=${min_endpoint_dist}\n"
        incr touching_count
      } elseif {$min_endpoint_dist <= 20.0} {
        append near_wires "wire\[$i\] (${wx1},${wy1})-(${wx2},${wy2}) net=${lab} endpoint_dist=${min_endpoint_dist}\n"
        incr near_count
      }
    }

    # Build diagnosis
    set diagnosis {}
    if {$touching_count > 0} {
      set diagnosis "Pin IS connected: $touching_count wire(s) touch the pin."
    } elseif {$near_count > 0} {
      set diagnosis "Pin NOT connected but $near_count wire(s) are NEAR (within 20 units). Likely a coordinate mismatch -- wire endpoint doesn't land exactly on pin. Use xschem.wire_to_pin to connect precisely."
    } else {
      set diagnosis "Pin NOT connected: no wires within 20 units of pin. No wire has been drawn to this pin yet. Use xschem.wire_to_pin or xschem.wire to create a connection."
    }

    if {$net ne {} && ![string match {#net*} $net]} {
      append diagnosis " Netlister assigned net='$net'."
    } elseif {[string match {#net*} $net]} {
      append diagnosis " Netlister assigned auto-net='$net' (indicates unconnected or floating)."
    } else {
      append diagnosis " Netlister assigned no net (disconnected)."
    }

    mcp::ok [list \
      instance $instance_name \
      pin $pin_name \
      pin_x $pin_x \
      pin_y $pin_y \
      pin_dir $dir \
      assigned_net $net \
      touching_wire_count $touching_count \
      touching_wires [string trim $touching_wires] \
      near_wire_count $near_count \
      near_wires [string trim $near_wires] \
      total_wires $n_wires \
      diagnosis $diagnosis]
  } result]} {
    return [mcp::err debug_pin_wire_connection_error $result]
  }
  return $result
}

proc mcp_force_pin_net {instance_name pin_name net_name} {
  if {[catch {
    if {[string trim $instance_name] eq {}} {
      error "instance_name is required"
    }
    if {[string trim $pin_name] eq {}} {
      error "pin_name is required"
    }
    if {[string trim $net_name] eq {}} {
      error "net_name is required"
    }
    set coord_result [xschem instance_pin_coord $instance_name name $pin_name]
    if {$coord_result eq {}} {
      error "pin '$pin_name' not found on instance '$instance_name'"
    }
    set pin_x [lindex $coord_result 1]
    set pin_y [lindex $coord_result 2]
    set old_net [xschem instance_net $instance_name $pin_name]

    set safe_inst [regsub -all {[^a-zA-Z0-9_]} $instance_name {_}]
    set safe_pin [regsub -all {[^a-zA-Z0-9_]} $pin_name {_}]
    set label_name "netlabel_${safe_inst}_${safe_pin}"
    xschem instance lab_pin.sym $pin_x $pin_y 0 0 "name=${label_name} lab=${net_name}"
    xschem redraw

    mcp::ok [list \
      instance $instance_name \
      pin $pin_name \
      net_name $net_name \
      pin_x $pin_x \
      pin_y $pin_y \
      previous_net $old_net \
      label_instance $label_name \
      method {placed lab_pin.sym at pin coordinates with lab=net_name}]
  } result]} {
    return [mcp::err force_pin_net_error $result]
  }
  return $result
}

proc mcp_get_netlist_trace {} {
  if {[catch {
    # Generate a fresh netlist to ensure node resolution is current
    mcp::ensure_netlist_dir
    set erc_messages [xschem netlist -messages]

    set n_inst [xschem get instances]
    set instance_trace {}
    for {set i 0} {$i < $n_inst} {incr i} {
      set coord [xschem instance_coord $i]
      set inst_name [lindex $coord 0]
      set sym_name [lindex $coord 1]
      set nodemap [xschem instance_nodemap $i]
      append instance_trace "--- ${inst_name} (${sym_name}) ---\n"
      set nm_items [lrange $nodemap 1 end]
      foreach {pin net} $nm_items {
        set flag {}
        if {$net eq {} || $net eq {NULL}} {
          set flag " *** DISCONNECTED ***"
        } elseif {[string match {#net*} $net]} {
          set flag " *** AUTO-NET (likely unconnected) ***"
        }
        append instance_trace "  ${pin} -> ${net}${flag}\n"
      }
    }

    set n_wires [xschem get wires]
    set wire_trace {}
    set unlabeled_count 0
    for {set i 0} {$i < $n_wires} {incr i} {
      set coords [xschem wire_coord $i]
      set x1 [lindex $coords 0]
      set y1 [lindex $coords 1]
      set x2 [lindex $coords 2]
      set y2 [lindex $coords 3]
      set lab [xschem getprop wire $i lab]
      if {$lab eq {}} {
        set lab {(unlabeled)}
        incr unlabeled_count
      }
      append wire_trace "wire\[$i\] (${x1},${y1})-(${x2},${y2}) -> ${lab}\n"
    }

    set netlist_file [mcp::default_netlist_file]
    set netlist_snippet {}
    if {[file exists $netlist_file]} {
      set fd [open $netlist_file r]
      set contents [read $fd]
      close $fd
      set all_lines [split $contents "\n"]
      set total_lines [llength $all_lines]
      if {$total_lines > 80} {
        set netlist_snippet [join [lrange $all_lines 0 79] "\n"]
        append netlist_snippet "\n... (truncated, $total_lines total lines) ..."
      } else {
        set netlist_snippet $contents
      }
    } else {
      set netlist_snippet "(netlist file not found at $netlist_file)"
    }

    mcp::ok [list \
      total_instances $n_inst \
      total_wires $n_wires \
      unlabeled_wires $unlabeled_count \
      erc_messages $erc_messages \
      instance_node_map [string trim $instance_trace] \
      wire_net_map [string trim $wire_trace] \
      netlist_snippet $netlist_snippet]
  } result]} {
    return [mcp::err get_netlist_trace_error $result]
  }
  return $result
}
