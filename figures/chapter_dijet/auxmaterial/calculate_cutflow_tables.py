from cutflow_values import dict_mc16a, dict_mc16d, dict_mcTotal, dict_data15, dict_data16, dict_data17, dict_dataTotal, dict_sig_250, dict_sig_550
from math import log10, floor

# Removed total and GRL from these due to meaninglessness of numbers before trigger.

cuts_list_data = ["trigger","cleaning","njet","ngamma","photonpt","leadjet","subleadjet","ystar","mjj_inclusive","mjj_tagged"]

cuts_list_mc = ["trigger","cleaning","njet","ngamma","photonpt","leadjet","subleadjet","ystar","mjj_inclusive","mjj_tagged"]

cuts_names = {
  "total" : "Total",
  "GRL" : "Good runs list",
  "trigger" : "Trigger",
  "cleaning" : "Cleaning",
  "njet" : "n$_{\mathrm{jets}} \geq 2$",
  "ngamma" : "n$_{\gamma} \geq 1$",
  "photonpt" : "Lead $\gamma$ \pt cut",
  "leadjet" : "Lead jet \pt cut",
  "subleadjet" : "Sublead jet \pt cut",
  "ystar" : "$|y^{\\ast}| < 0.75$",
  "mjj_inclusive" : "Minimum \mjj",
#  "tagging" : "2 \\btagged",
#  "mjj_tagged" : "Minimum \mjj (tagged)"
  "mjj_tagged" : "2 $b$-tags"
}

# What lumi to scale MC tables to? In ipb.
# Thus this is to use 1 ifb:
scaleMC = 1000.0

def printTableHeader(caption,shortcaption) :
  print """
\\begin{table}[!h]
\setlength{\\tabcolsep}{10pt}
	\centering
	\caption["""+shortcaption+"""]{"""+caption+"""}
	\\begin{tabular}{ l | c c | c c}
		\\toprule
		& \multicolumn{2}{c}{Single photon trigger} & \multicolumn{2}{c}{Compound trigger} \\\\
		Cut & Events remaining & \% remaining & Events remaining & \% remaining \\\\
		\midrule"""


def printTableFooter(label) :
  print """		\\bottomrule
	\end{tabular}
	\label{"""+label+"""}
\end{table}
"""

lumiDict = {
    "compound_trigger" : {
        "2015" : 0.0,
        "2016" : 33.009,
        "2017" : 43.586,
    },

    "single_trigger" : {
        "2015" : 3.222,
        "2016" : 33.018,
        "2017" : 43.586,
    },
}

def getmc16amc16dval(trigger, mc16aval, mc16dval) :
  theselumis = lumiDict[trigger]
  denominator = theselumis["2015"]+theselumis["2016"]+theselumis["2017"]
  scale_mc16a = (theselumis["2015"]+theselumis["2016"])/denominator
  scale_mc16d = theselumis["2017"]/denominator

  # Currently each is normalised to 1 pb.
  # Need to combine them to a total which
  # is still 1 pb.

  mc16a_scaled = mc16aval * scale_mc16a
  mc16d_scaled = mc16dval * scale_mc16d
  total = mc16a_scaled + mc16d_scaled
  return total

## Functions for rounding correctly according to ATLAS guidelines:
# https://cds.cern.ch/record/1668799?
# These are tables, so the recommended procedure is to keep
# 2 sig. figs. in the uncertainty value and then
# round the central value to the same precision.
def roundPMValue(pmval) :
  # Order:
  order = int(floor(log10(abs(pmval))))
  # But we actually want one more than order for 2:
  rounded = round(pmval, -order+1)
  # If this is greater than or equal to order 0, we should be using an int.
  if order-1 > -1 :
    rounded = int(rounded)
    stringversion = "{0}".format(rounded)
  # Want to return a string with the rounded value
  # padded on the right with zeros as necessary
  else :
    precision = '.{0}f'.format(-order+1)
    stringversion = format(rounded, precision)
  return stringversion,order-1

# Now we need to get central value to same precision
# as the uncertainty. Second argument sets the order
# of the last known value in the uncertainty.
def roundCentralValue(val,precision) :
  val = round(val,-precision)
  if precision > -1 :
    val = int(val)
    stringversion = "{0}".format(val)
  else :
    precisionformula = '.{0}f'.format(-precision)
    stringversion = format(val, precisionformula)
  return stringversion

## Start with data table: easiest.
prevNumberSingle = None
prevNumberCompound = None
printTableHeader("Selections placed on the data samples after pre-selection requirements, as described in the main text, and the numbers of events that satisfy each successive requirement. \cutcomment. The percentages of remaining events are calculated relative to the previous line. The initial number of events for the combined trigger is smaller than for the single photon trigger because no combined trigger existed for the portion of the data collected in 2015.","Data cutflow")
for cut in cuts_list_data :
  # Currently skipping total and GRL. 
  if "total" in cut or "GRL" in cut : continue

  print "\t\t",cuts_names[cut]," & ",
  # Sum across years
  # No longer necessary as of nov. 10
  #nEvtSingle = dict_data15["single_trigger"][cut] + dict_data16["single_trigger"][cut] + dict_data17["single_trigger"][cut]
  nEvtSingle = dict_dataTotal["single_trigger"][cut]
  print int(nEvtSingle)," & ",
  # Round percentages the way we round errors: two sig figs.    
  if prevNumberSingle :
    print "$",roundPMValue(nEvtSingle/prevNumberSingle * 100.0)[0], "\\%$ & ",
  else :
    print "-- & ",
  #nEvtCompound = dict_data15["compound_trigger"][cut] + dict_data16["compound_trigger"][cut] + dict_data17["compound_trigger"][cut]
  nEvtCompound = dict_dataTotal["compound_trigger"][cut]
  print int(nEvtCompound)," & ",
  # Round percentages the way we round errors: two sig figs.      
  if prevNumberCompound :
    print "$",roundPMValue(nEvtCompound/prevNumberCompound * 100.0)[0], "\\%$ \\\\"
  else :
    print "-- \\\\"
  prevNumberSingle = nEvtSingle
  prevNumberCompound = nEvtCompound
  # For dividing tagged from inclusive
  if "mjj_inclusive" in cut :
    print "\t\t\\midrule"
printTableFooter("tabaux:cutflow_data")

## Next: mc16a+mc16d.
## Originally required lumi scaling (function still available)
## But current numbers also come already added. Stick with that for now.
prevNumberSingle = None
prevNumberCompound = None
printTableHeader("Selections placed on the samples of simulated background events after pre-selection requirements, as described in the main text, and the numbers of events that satisfy each successive requirement. \cutcomment. The percentages of remaining events are calculated relative to the previous line. The samples consist of multijet + $\gamma$ processes, simulated as described in~\cref{sec:background}, with the total event yield normalised to 1 fb$^{-1}$ of integrated luminosity.","MC cutflow")
for cut in cuts_list_mc :
  print "\t\t",cuts_names[cut]," & ",
  nEvtSinglePMOriginal = dict_mcTotal["single_trigger_pm"][cut]*scaleMC
  nEvtSinglePM,precision = roundPMValue(nEvtSinglePMOriginal)
  nEvtSingleOriginal = dict_mcTotal["single_trigger"][cut]*scaleMC
  nEvtSingle = roundCentralValue(nEvtSingleOriginal,precision)
  print "$",nEvtSingle,"\pm",nEvtSinglePM,"$ & ",
  # Round percentages the way we round errors: two sig figs.
  if prevNumberSingle :
    print "$",roundPMValue(nEvtSingleOriginal/prevNumberSingle * 100.0)[0], "\\%$ & ",
  else :
    print "-- & ",
  nEvtCompoundPMOriginal = dict_mcTotal["compound_trigger_pm"][cut]*scaleMC
  nEvtCompoundPM,precision = roundPMValue(nEvtCompoundPMOriginal)
  nEvtCompoundOriginal = dict_mcTotal["compound_trigger"][cut]*scaleMC
  nEvtCompound = roundCentralValue(nEvtCompoundOriginal,precision)
  print "$",nEvtCompound,"\pm",nEvtCompoundPM,"$ & ",
  # Round percentages the way we round errors: two sig figs.  
  if prevNumberCompound :
    print "$",roundPMValue(nEvtCompoundOriginal/prevNumberCompound * 100.0)[0], "\\%$ \\\\"
  else :
    print "-- \\\\"
  prevNumberSingle = nEvtSingleOriginal
  prevNumberCompound = nEvtCompoundOriginal
  if "mjj_inclusive" in cut :
    print "\t\t\\midrule"  
printTableFooter("tabaux:cutflow_mc")

## Signal 1: 250 GeV.
prevNumberSingle = None
prevNumberCompound = None
printTableHeader("Selections placed on the samples of simulated $Z^\prime$ events where $m_{Z'} = 250\,\GeV$, after pre-selection requirements as described in the main text. Also shown is the number of events that satisfy each successive requirement. Percentages remaining are relative to the previous cut, and all values are relative to the objects remaining after a baseline pre-selection. \cutcomment.","MC $m_{Z'} = 250\,\GeV$ cutflow")
for cut in cuts_list_mc :
  print "\t\t",cuts_names[cut]," & ",
  nEvtSinglePMOriginal = dict_sig_250["single_trigger_pm"][cut]*scaleMC
  nEvtSinglePM,precision = roundPMValue(nEvtSinglePMOriginal)
  nEvtSingleOriginal = dict_sig_250["single_trigger"][cut]*scaleMC
  nEvtSingle = roundCentralValue(nEvtSingleOriginal,precision)
  print "$",nEvtSingle,"\pm",nEvtSinglePM,"$",
  # Round percentages the way we round errors: two sig figs.    
  if cuts_list_mc.index(cut) == 0 :
    print " & -- & ",
  else :  
    print " & {0}\% & ".format(roundPMValue(nEvtSingleOriginal/prevNumberSingle * 100.0)[0]),
  nEvtCompoundPMOriginal = dict_sig_250["compound_trigger_pm"][cut]*scaleMC
  nEvtCompoundPM,precision = roundPMValue(nEvtCompoundPMOriginal)
  nEvtCompoundOriginal = dict_sig_250["compound_trigger"][cut]*scaleMC
  nEvtCompound = roundCentralValue(nEvtCompoundOriginal,precision)
  print "$",nEvtCompound,"\pm",nEvtCompoundPM,"$",
  # Round percentages the way we round errors: two sig figs.      
  if cuts_list_mc.index(cut) == 0 :
    print " & -- \\\\ "
  else :
    print " & {0}\% \\\\ ".format(roundPMValue(nEvtCompoundOriginal/prevNumberCompound * 100.0)[0])
  prevNumberSingle = nEvtSingleOriginal
  prevNumberCompound = nEvtCompoundOriginal    
  if "mjj_inclusive" in cut :
    print "\t\t\\midrule"    
printTableFooter("tabaux:cutflow_zprime_250")

## Signal 2: 550 GeV.
prevNumberSingle = None
prevNumberCompound = None
printTableHeader("Selections placed on the samples of simulated $Z^\prime$ events where $m_{Z'} = 550\,\GeV$, after pre-selection requirements as described in the main text. Also shown is the number of events that satisfy each successive requirement. Percentages remaining are relative to the previous cut, and all values are relative to the objects remaining after a baseline pre-selection. \cutcomment.","MC $m_{Z'} = 550\,\GeV$ cutflow")
for cut in cuts_list_mc :
  print "\t\t",cuts_names[cut]," & ",
  nEvtSinglePMOriginal = dict_sig_550["single_trigger_pm"][cut]*scaleMC
  nEvtSinglePM,precision = roundPMValue(nEvtSinglePMOriginal)
  nEvtSingleOriginal = dict_sig_550["single_trigger"][cut]*scaleMC
  nEvtSingle = roundCentralValue(nEvtSingleOriginal,precision)  
  print "$",nEvtSingle, "\pm",nEvtSinglePM,"$",
  # Round percentages the way we round errors: two sig figs.      
  if cuts_list_mc.index(cut) == 0 :
    print " & -- & ",
  else :  
    print " & {0}\% & ".format(roundPMValue(nEvtSingleOriginal/prevNumberSingle * 100.0)[0]),
  nEvtCompoundPMOriginal = dict_sig_550["compound_trigger_pm"][cut]*scaleMC
  nEvtCompoundPM,precision = roundPMValue(nEvtCompoundPMOriginal)
  nEvtCompoundOriginal = dict_sig_550["compound_trigger"][cut]*scaleMC
  nEvtCompound = roundCentralValue(nEvtCompoundOriginal,precision)    
  print "$",nEvtCompound, "\pm",nEvtCompoundPM,"$",
  # Round percentages the way we round errors: two sig figs.      
  if cuts_list_mc.index(cut) == 0 :
    print " & -- \\\\ "
  else :
    print " & {0}\% \\\\ ".format(roundPMValue(nEvtCompoundOriginal/prevNumberCompound * 100.0)[0])
  prevNumberSingle = nEvtSingleOriginal
  prevNumberCompound = nEvtCompoundOriginal    
  if "mjj_inclusive" in cut :
    print "\t\t\\midrule"    
printTableFooter("tabaux:cutflow_zprime_550")


