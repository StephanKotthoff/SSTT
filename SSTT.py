import tkinter as tk
import os
import json
import copy
from tkinter import font
from iapws import IAPWS97

class radiobutton(tk.Frame):
      def __init__(self, parent=None, picks=[], property_str=[],**kwargs):
            if kwargs["input_output"]=="input":
                  tk.Frame.__init__(self, parent,bg="tomato")
            if kwargs["input_output"]=="output":
                  tk.Frame.__init__(self, parent,bg="light grey")

            self._var = tk.StringVar()
            self._var.set(0)
            self._var.trace("w", self.trace_fun)
            if kwargs["input_output"]=="input":
                  self.property_label=tk.Label(self,bg="tomato",text=property_str,font=courier_small)
                  self.property_entry=tk.Entry(self,bg="yellow",font=courier_small, width=10, justify=tk.RIGHT)
            if kwargs["input_output"]=="output":
                  self.property_label=tk.Label(self,bg="light grey",text=property_str,font=courier_small)
                  self.property_entry=tk.Entry(self,bg="dark grey",font=courier_small, width=10, justify=tk.RIGHT)

            col_index=0
            self.property_label.grid(row=0,column=col_index)
            col_index+=1
            self.property_entry.grid(row=0,column=col_index)
            
            col_index+=1
            self._var.set(picks[0])
            for pick in picks:
                  if kwargs["input_output"]=="input":
                        chk = tk.Radiobutton(self,bg="tomato", activebackground="tomato", text=pick, value=pick, variable=self._var, font=courier_small)
                  if kwargs["input_output"]=="output":
                        chk = tk.Radiobutton(self,bg="light grey", activebackground="light grey", text=pick, value=pick, variable=self._var, font=courier_small)
                  chk.grid(row=0,column=col_index)
                  col_index+=1

      def trace_fun(self, *args):
            return self._var.get()

class checkbar(tk.Frame):
      def __init__(self, parent=None, picks=[]):
            tk.Frame.__init__(self, parent,bg="chocolate")
            self.auswahl=picks
            self.vars = []
            row_index=0
            for pick in picks:
                  var = tk.IntVar()
                  chk = tk.Checkbutton(self, text=pick, variable=var, bg="chocolate", activebackground="chocolate", font=courier_small)
                  chk.grid(row=row_index,column=0,sticky=tk.W)
                  self.vars.append(var)
                  row_index+=1
      def state(self):
            return list(map((lambda var: var.get()), self.vars))

def calculate_values_SI(property_input=[],value_input=[], unit_input=[]):
      factor_input=[0,0]
      offset_input=[0,0]
      for indx in range(len(property_input)):
            for key,value in unit_conversion.items():
                  unit_sel=key.split("_")
                  if unit_input[indx]==unit_sel[0]:
                        factor_input[indx]=value[0]
                        offset_input[indx]=value[1]
      values_input_final={}
      values_output_SI={}
      try:
            for indx in range(len(property_input)):
                  values_input_final[property_input[indx]]=[float(value_input[indx]),float(offset_input[indx]),float(factor_input[indx])]
            for key in values_input_final:
#           some manual entries...
#           properties_units_input=["Enthalpy","Pressure","Temperature","Steam Quality","Entropy"]
                  if key=="Specific Enthalpy":
                        enthalpy_val_input=(values_input_final[key][0]+values_input_final[key][1])*values_input_final[key][2]
                  if key=="Pressure":
                        pressure_val_input=(values_input_final[key][0]+values_input_final[key][1])*values_input_final[key][2]
                  if key=="Temperature":
                        temperature_val_input=(values_input_final[key][0]+values_input_final[key][1])*values_input_final[key][2]
                  if key=="Specific Entropy":
                        entropy_val_input=(values_input_final[key][0]+values_input_final[key][1])*values_input_final[key][2]
                  if key=="Steam Quality":
                        steamquality_val_input=(values_input_final[key][0]+values_input_final[key][1])*values_input_final[key][2]

            if values_input_final.get("Temperature") and values_input_final.get("Pressure"):
                  water_steam=IAPWS97(T=temperature_val_input, P=pressure_val_input)
            if values_input_final.get("Pressure") and values_input_final.get("Specific Enthalpy"):
                  water_steam=IAPWS97(P=pressure_val_input, h=enthalpy_val_input)
            if values_input_final.get("Pressure") and values_input_final.get("Specific Entropy"):
                  water_steam=IAPWS97(P=pressure_val_input, s=entropy_val_input)
            if values_input_final.get("Specific Enthalpy") and values_input_final.get("Specific Entropy"):
                  water_steam=IAPWS97(h=enthalpy_val_input, s=entropy_val_input)
            if values_input_final.get("Temperature") and values_input_final.get("Steam Quality"):
                  water_steam=IAPWS97(T=temperature_val_input, x=steamquality_val_input)
            if values_input_final.get("Pressure") and values_input_final.get("Steam Quality"):
                  water_steam=IAPWS97(P=pressure_val_input, x=steamquality_val_input)
            values_output_SI["Specific Enthalpy"]=[water_steam.h,"kJ/kg"]
            values_output_SI["Pressure"]=[water_steam.P,"MPa"]
            values_output_SI["Temperature"]=[water_steam.T,"K"]
            values_output_SI["Specific Entropy"]=[water_steam.s,"kJ/kgK"]
            values_output_SI["Specific Volume"]=[water_steam.v,"m3/kg"]
            values_output_SI["Density"]=[water_steam.rho,"kg/m3"]
            values_output_SI["Steam Quality"]=[water_steam.x,"kg/kg"]
      except:
            values_output_SI["Specific Enthalpy"]="ERROR"
            values_output_SI["Pressure"]="ERROR"
            values_output_SI["Temperature"]="ERROR"
            values_output_SI["Specific Entropy"]="ERROR"
            values_output_SI["Specific Volume"]="ERROR"
            values_output_SI["Density"]="ERROR"
            values_output_SI["Steam Quality"]="ERROR"

      return values_output_SI            

def calculate_values_final(values_output_SI={}):
      for key_dict in values_output_SI:
            try:
                  for key,value in unit_conversion.items():
                        unit_sel=key.split("_")
                        if values_output_SI[key_dict][1]==unit_sel[0]:
                              factor_output=1/value[0]
                              offset_output=-value[1]
                  final_value=(values_output_SI[key_dict][0]+offset_output)*factor_output
                  values_output_SI[key_dict][0]=final_value
            except:
                  values_output_SI[key_dict][0]="ERROR"

      values_output_final={}
      values_output_final=values_output_SI

      return values_output_final       

def allstates():
#     selection of properties to be calculated
      input_property_calculate_list=input_property_calculate.state()
      input_property_calculate_list_properties=['prop1','prop2']
      counter=0
      if input_property_calculate_list.count(1)==2:
            for indx in range(len(input_property_calculate_list)):
                  if input_property_calculate_list[indx]==1:
                        input_property_calculate_list_properties[counter]=properties_units_input[indx]
                        counter+=1
#     if selection !=2 then set properties to first 2 (here: Enthalpy, Pressure)
      if input_property_calculate_list.count(1)!=2:
            input_property_calculate_list_properties[0]=properties_units_input[0]
            input_property_calculate_list_properties[1]=properties_units_input[1]

#     assignment of properties to be calculated
      properties_input_select=input_property_calculate_list_properties
      property_input=["property_1","property_2"]
      value_input=[0,0]
      unit_input=["unit_1","unit_2"]
      for key_dict in properties_units:
            for indx in range(len(properties_input_select)):
                  if key_dict==properties_input_select[indx]:
                        try:
                              value_input[indx] = float(input_property[key_dict].property_entry.get())
                        except:
#     if float not possible => value =-1
                              value_input[indx]=-1
                        if value_input[indx]>=0:
#     for value, unit and property single lists. could be done with dictionary.
                              unit_input[indx]=str(input_property[key_dict].trace_fun()).strip() #get value and delete all empty spaces of string
                              property_input[indx]=properties_input_select[indx]

#     calculate
      calculated_values_SI=calculate_values_SI(property_input,value_input,unit_input) #return dictionary
      transform_output_values_SI={}
      for key_dict in output_property:
            try:
                  transform_output_values_SI[key_dict]=[calculated_values_SI[key_dict][0],str(output_property[key_dict].trace_fun()).strip()] #get value and delete all empty spaces of string
            except:
                  transform_output_values_SI[key_dict]="ERROR"

      values_output_final={}
      values_output_final=calculate_values_final(transform_output_values_SI)
#            print("calculated values SI: ",calculated_values_SI)
#            print("calculated values final units: ",values_output_final)
      for key_dict in output_property:
            output_property[key_dict].property_entry.delete(0, tk.END)
            
            calculated_number=values_output_final[key_dict][0]
            calculated_number_int=int(calculated_number)
            counting_numbers_max=5
            if calculated_number_int!=0:
                  calculated_number_int_len=len(str(calculated_number_int))
                  counting_numbers=counting_numbers_max-calculated_number_int_len
            else:
                  calculated_number_int_len=0
                  counting_numbers=counting_numbers_max-calculated_number_int_len
            total_len=calculated_number_int_len+counting_numbers+1
            final_number='{:{width}.{prec}f}'.format(calculated_number, width=calculated_number_int_len, prec=counting_numbers).ljust(total_len+counting_numbers_max-counting_numbers," ")
            output_property[key_dict].property_entry.insert(0,final_number)

if __name__ == '__main__':
      root = tk.Tk()
      root.title("Simple Steam Table Tool 2018-05-29 by S.Kotthoff")

      courier_small = font.Font(family="Courier",size=12,weight="normal")
      frame_1=tk.Frame(root,bg="dark grey",height=203, width=200)
#      frame_1.grid_propagate(0)
      frame_1.grid(row=1,column=1)
      frame_2=tk.Frame(root,bg="tomato")
      frame_2.grid(row=0,column=2)
      frame_3=tk.Frame(root,bg="light grey")
      frame_3.grid(row=1,column=2)
      frame_4=tk.Frame(root,bg="chocolate",height=145, width=200)
#      frame_4.grid_propagate(0)
      frame_4.grid(row=0,column=1)

#get all values from external dump files
#get current folder
      current_folder=os.path.abspath(os.path.dirname(__file__))
      with open(current_folder + '\\properties_units.dump') as f:
            properties_units = json.load(f)
      with open(current_folder + '\\unit_conversion.dump') as f:
            unit_conversion = json.load(f)
      with open(current_folder + '\\properties_units_input.dump') as f:
            properties_units_input = json.load(f)
      with open(current_folder + '\\properties_units_output.dump') as f:
            properties_units_output = json.load(f)

#     For alignment of values in frame: ljust all units in dictionary
#     updated_values_dict contains all values in a list which is passed to properties_units
      properties_units_update=copy.deepcopy(properties_units)
      for key_dict in properties_units_update:
            updated_values_dict=[]
            counter_updated_values_dict=0
            for value_single_dict in properties_units_update[key_dict]:
                  updated_values_dict.append(counter_updated_values_dict)
                  updated_values_dict[counter_updated_values_dict]=str(value_single_dict).ljust(7)
                  counter_updated_values_dict+=1
            properties_units_update[key_dict]=updated_values_dict

      input_property={}
      output_property={}
      row_counter_input=0
      row_counter_output=0
      for key_dict in properties_units_update:
#            print(key_dict) #with counter: print(list(properties_units_update.keys())[row_counter])
#            print(properties_units_update[key_dict]) #with counter: properties_units_update[list(properties_units_update.keys())[row_counter]]
            if properties_units_input.count(key_dict):
                  input_property[key_dict]=radiobutton(frame_2, list(properties_units_update[key_dict]), str(key_dict).ljust(18),input_output="input")
                  input_property[key_dict].grid(row=row_counter_input,column=0,sticky=tk.W)
                  row_counter_input+=1
            if properties_units_output.count(key_dict):
                  output_property[key_dict]=radiobutton(frame_3, list(properties_units_update[key_dict]), str(key_dict).ljust(18),input_output="output")
                  output_property[key_dict].grid(row=row_counter_output,column=0,sticky=tk.W)
                  row_counter_output+=1

      input_property_calculate = checkbar(frame_4, properties_units_input)
      input_property_calculate.grid(row=0,column=0)

      frame_2.update()
      frame_3.update()
      height_frame2=frame_2.winfo_height()
      height_frame3=frame_3.winfo_height()
      height_frame=height_frame2+height_frame3
      button_calc=tk.Button(frame_1, text='Calculate', command=allstates,font=courier_small)
      button_calc.place(in_=frame_1, anchor="c", relx=.5, rely=.5)

      root.mainloop()
