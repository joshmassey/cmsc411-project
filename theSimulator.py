import sys
from copy import deepcopy


class Instruction:
	"""docstring"""
	def __init__(self):
		self.lineNum = 0
		self.label = ""
		self.instruction = ""
		self.rawOperands = ""
		self.operands = [ "" for i in range(3) ]
		self.clockCycles = [ ]


class theSimulator:
	"""docstring for theSimulator"""
	def __init__(self, instructionFileName, dataFileName, outputFileName):
		self.theCommands = [ Instruction() for i in range(32) ]
		self.totalLines = 0
		self.registers = [ 0 for i in range(32) ]
		# self.pipelineClockCycles = [ "" for i in range(32) ]
		self.pipelineStages = ["IF", "ID", "EX1", "EX2", "EX3", "MEM", "WB"]
		self.pipeline = { "IF": Instruction(), "ID": Instruction(), "EX1": Instruction(), \
			"EX2": Instruction(), "EX3": Instruction(), "MEM": Instruction(), "WB": Instruction() }
		self.memory_data = [ Instruction() for i in range(32) ]
		self.instructionMemory = [ [ Instruction() for i in range(8) ] for i in range(2) ]
		# self.dataMemory = [ [ "" for i in range(4) ] for i in range(4) ]
		self.dataMemory = [ 0 for i in range(32) ]
		self.iCache_numAccesses = 0
		self.iCache_numMisses = 0
		self.dCache_numAccesses = 0
		self.dCache_numMisses = 0

		self.readInInstructions(instructionFileName)
		self.readInData(dataFileName)
		self.runSimulation()
		self.printOutput(outputFileName)
		

	def readInInstructions(self, fileName):
		self.totalLines = 0
		rawLines = []
		with open(fileName) as FILE:
			rawLines = FILE.readlines()
			FILE.close()
		
		# print("HET!")
		# print(len(rawLines))
		
		for line in range(len(rawLines)):
			rawLines[line] = rawLines[line].upper()
			token = ""
			inst_token=0
			# print("MY LINE IS:" + rawLines[line])
		
			i = 0
			while (i < len(rawLines[line])):
				# print(rawLines[line][i])
				# print(len(rawLines[line]))
				if ( (rawLines[line][i] != ' ') and (rawLines[line][i] != '\t') ):
					# print(i)
					token += rawLines[line][i]
					if (rawLines[line][i] == ':'):
						# print("HERE 1")
						self.theCommands[self.totalLines].label = token[0:-1]
						token = ""
					elif( (not inst_token) and ((i+1 >= len(rawLines[line]) or (rawLines[line][i+1] == ' ') or \
						(rawLines[line][i+1] == '\t')))):# or (rawLines[line][i+1] == 0))):
						# print("HERE 2")
						# print(self.totalLines)
						# print(self.totalLines)
						self.theCommands[self.totalLines].instruction = token
						# print(token)
						# sys.exit()
						self.theCommands[self.totalLines].lineNum = self.totalLines
						inst_token = 1
						token = ""
						self.totalLines += 1
						self.theCommands[self.totalLines-1].lineNum = self.totalLines
					elif( (inst_token) and (rawLines[line][i] != 0) ):
						# print("HERE 3")
						self.theCommands[self.totalLines-1].rawOperands = rawLines[line][i:len(rawLines[line])-1]
						# print(self.theCommands[self.totalLines-1].rawOperands)
						# sys.exit()
						# print("OP " + self.theCommands[self.totalLines-1].rawOperands)
						i = len(rawLines[line]) - 1
						inst_token = 0
					# else:
					# 	try:
							
					# 	except IndexError:
					# 		continue
				i += 1


	def readInData(self, fileName):
		with open(fileName) as FILE:
			self.theData = FILE.readlines()
			FILE.close()

		for i in self.theData:
			i = int(i,2)


	def printOutput(self, fileName):
		runningString = "Line #" + "\t" + "Label" + "\t" + "Operation" + "\t\t\tIF\tID\tEX\tMEM\tWB\n"
		for command in self.theCommands:
			if (command.lineNum != 0):
				runningString += str(command.lineNum)
				if (command.label == ""):
					runningString += "\t\t\t\t"
				else:
					if (len(command.label + ":") < 4):
						runningString += "\t\t" + str(command.label) + ":\t\t"
					else:
						runningString += "\t\t" + str(command.label) + ":\t"
				runningString += command.instruction + " "
				if (len(command.instruction + " " + str(command.rawOperands)) < 4):
					runningString += str(command.rawOperands) + "\t\t\t\t\t"
				elif (len(command.instruction + " " + str(command.rawOperands)) < 8):
					runningString += str(command.rawOperands) + "\t\t\t\t"
				elif (len(command.instruction + " " + str(command.rawOperands)) < 12):
					runningString += str(command.rawOperands) + "\t\t\t"
				elif (len(command.instruction + " " + str(command.rawOperands)) < 16):
					runningString += str(command.rawOperands) + "\t\t"
				else:
					runningString += str(command.rawOperands) + "\t"
				# runningString += self.pipelineClockCycles[i] + "\n"
				for cycle in command.clockCycles:
					runningString += str(cycle) + "\t"
				runningString += "\n"
				# runningString += self.pipelineClockCycles[i] + "\n"
		
		# print(type(self.pipelineClockCycles[i]))
		runningString += "\n\nTotal number of access requests for instruction cache: " \
			+ str(self.iCache_numAccesses) + "\n" \
			+ "Number of instruction cache hits: " \
			+ str(self.iCache_numAccesses - self.iCache_numMisses) + "\n\n" \
			+ "Total number of access requests for data cache: " \
			+ str(self.dCache_numAccesses) + "\n" \
			+ "Number of data cache hits: " \
			+ str(self.dCache_numAccesses - self.dCache_numMisses) + "\n\n"

		# print(runningString)
		print("Output successfully written to " + fileName)
		outFile = open(fileName, 'w')
		outFile.write(runningString)
		outFile.close()


	def runSimulation(self):
		currLine = 0
		cycle = 0
		cyclesPop = -1
		counter = -1
		while( (currLine == 0) or (self.notHalt()) ):
			# print("HERE 1!")
			cycle += 1
			# print("cyclesPop" + str(cyclesPop))
			if( (not self.getInstruction(currLine)) and (cyclesPop < 0) ):
				# print("I CRAZILY WENT HERE!")
				cyclesPop = 23
				# print("HERE 2!")
			# print("cyclesPop" + str(cyclesPop))

			self.clearController(cycle)
			self.pipelineControllerWB(cycle)
			self.pipelineControllerMEM(cycle)
			self.pipelineControllerEX3(cycle)
			self.pipelineControllerEX2(cycle)
			self.pipelineControllerEX1(cycle)
			jumping, pc_branch = self.pipelineControllerID(currLine, cycle)
			currLine = self.pipelineControllerIF(currLine, cycle)

			# currLine = self.pipelineControllerIF(currLine, cycle)
			# jumping, pc_branch = self.pipelineControllerID(currLine, cycle)
			# self.pipelineControllerEX1(cycle)
			# self.pipelineControllerEX2(cycle)
			# self.pipelineControllerEX3(cycle)
			# self.pipelineControllerMEM(cycle)
			# self.pipelineControllerWB(cycle)
			# self.clearController(cycle)

			if (jumping):
				# print(currLine, pc_branch)
				# cycle -= 1
				# self.pipelineClockCycles[self.pipeline["IF"].lineNum-1] += str(cycle) + "\t"
				# self.pipelineClockCycles[self.pipeline["ID"].lineNum-1] += str(cycle) + "\t"
				self.theCommands[ self.pipeline["IF"].lineNum-1 ].clockCycles.append(cycle)
				self.theCommands[ self.pipeline["ID"].lineNum-1 ].clockCycles.append(cycle)
				currLine = pc_branch
				self.pipeline["IF"] = Instruction()
				self.pipeline["ID"] = Instruction()
				counter = 0

				# sys.exit()
			if (cyclesPop == 0):
				# print("I WENT HERE!")
				self.popInstructionCache(currLine, cycle)
				cyclesPop -= 1
				# counter += 1
			elif (cyclesPop > 0):
				cyclesPop -= 1
			
			if (counter > -1):
				counter += 1
			if (counter == 5):
				sys.exit()

		self.pipeline["IF"].lineNum = 0
		self.pipeline["ID"].lineNum = 0
		self.pipeline["EX1"].lineNum = 0
		while ( self.registerEmpty() ):
			cycle += 1
			self.clearController(cycle)
			self.pipelineControllerWB(cycle)
			self.pipelineControllerMEM(cycle)
			self.pipelineControllerEX3(cycle)
			self.pipelineControllerEX2(cycle)
			self.pipelineControllerEX1(cycle)


	def notHalt(self):
		# print("notHalt!")
		result = 0
		if (self.pipeline["EX1"].instruction != "HLT"):
			result = 1
		# print(self.pipeline["EX1"].instruction == "HLT")
		# sys.exit()
		# print(result)
		return result


	def getInstruction(self, currLine):
		# print("getInstruction!" + str(currLine))
		block = (currLine // 8) % 2
		word = currLine % 8
		# print(block, word)
		# print(self.instructionMemory[block][word].lineNum)
		# print(self.theCommands[currLine].lineNum)
		if (self.instructionMemory[block][word].lineNum == self.theCommands[currLine].lineNum):
			return 1
		else:
			return 0


	def popInstructionCache(self, currLine, cycle):
		# print("popInstructionCache!" + str(cycle) + " " + str(currLine))
		block = (currLine // 8) % 2
		word = (currLine // 8) * 8
		# print(block, word)
		self.iCache_numMisses += 1
		# print("Populating instructions " + str(cycle))
		for i in range(8):
			# print(self.theCommands[word+i].lineNum)
			self.instructionMemory[block][i] = self.theCommands[word+i]
		# sys.exit()
		return cycle


	def pipelineShift(self, stage):
		prevStage = self.pipelineStages[ self.pipelineStages.index(stage)-1 ]
		# print("pipelineShift!" + str(stage))
		# print("B4 -- self.pipeline[stage].lineNum\t" + str(self.pipeline[stage].lineNum))
		# print("B4 -- self.pipeline[prevStage].lineNum\t" + str(self.pipeline[prevStage].lineNum))
		if ( (self.pipeline[stage].lineNum == 0) and (self.pipeline[prevStage].lineNum != 0) ):
			# print("THIS IS SET!")
			self.pipeline[stage] = deepcopy(self.pipeline[prevStage])
			self.pipeline[prevStage].lineNum = 0
			# print("self.pipeline[stage].lineNum\t" + str(self.pipeline[stage].lineNum))
			# print("self.pipeline[prevStage].lineNum\t" + str(self.pipeline[prevStage].lineNum))
			return 1
		return 0


	def decode(self, line):
		# print("decode!" + str(line))
		if (line.instruction == "LI"):
			findComma = line.rawOperands.index(",")
			line.operands[0]=line.rawOperands[ : findComma ]
			line.operands[1]=line.rawOperands[ findComma+2 : ]
			# print(line.instruction + "\n" + line.operands[0] + "\n" + line.operands[1] )#+ "\n")
			# sys.exit()
		elif ( (line.instruction == "ADDI") or (line.instruction == "SUBI") or (line.instruction == "ANDI") \
			or (line.instruction == "ORI") or (line.instruction == "BEQ") or (line.instruction == "BNE") or (line.instruction == "MULTI") ):
			findComma = line.rawOperands.index(",")
			findSecondComma = findComma + (line.rawOperands[ findComma+1 : ]).index(",") + 1
			line.operands[0] = line.rawOperands[ : findComma ]
			line.operands[1] = line.rawOperands[ findComma+2 : findSecondComma ]
			line.operands[2] = line.rawOperands[ findSecondComma+2 : ]
			# print(line.instruction + "\n" + line.operands[0] + "\n" + line.operands[1] + "\n" + line.operands[2])# + "\n")
			# sys.exit()
		elif ( (line.instruction == "LW") or (line.instruction == "SW")):
			findComma = line.rawOperands.index(",")
			findLParen = line.rawOperands.index("(")
			line.operands[0] = line.rawOperands[0:findComma]
			line.operands[1] = line.rawOperands[findLParen-1:findLParen]
			line.operands[2] = line.rawOperands[findLParen+1:findLParen+3]
			# print(line.instruction + "\n" + line.operands[0] + "\n" + line.operands[1] + "\n" + line.operands[2])# + "\n")
			# print(line.rawOperands)
			# sys.exit()
		elif ( (line.instruction == "ADD") or (line.instruction == "SUB") or (line.instruction == "OR") \
			or (line.instruction == "AND") or (line.instruction == "MULT")):
			findComma = line.rawOperands.index(",")
			findSecondComma = findComma + (line.rawOperands[ findComma+1 : ]).index(",") + 1
			line.operands[0] = line.rawOperands[ : findComma ]
			line.operands[1] = line.rawOperands[ findComma+2 : findSecondComma ]
			line.operands[2] = line.rawOperands[ findSecondComma+2 : ]
			# print(line.instruction + "\n" + line.operands[0] + "\n" + line.operands[1] + "\n" + line.operands[2])# + "\n")
			# sys.exit()
		elif (line.instruction == "J"):
			line.operands[0] = line.rawOperands
			# print(line.instruction + "\n" + line.operands[0])# + "\n")
			# sys.exit()
		elif (line.instruction == "HLT"):
			pass
		else:
			print("Could not interpret the operation \"" + line.instruction \
				+ "of the command \"" + line.instruction + " " + line.rawOperands + "\"\n" \
				+ "....Now terminating the program")
			sys.exit()


	def pipelineControllerIF(self, currLine, cycle):
		# print("HERE!")
		block = (currLine // 8) % 2
		word = currLine % 8
		if ( (self.pipeline["IF"].lineNum == 0) and (self.instructionMemory[block][word].lineNum == (currLine+1)) ):
			# self.theCommands[ self.pipeline["IF"].lineNum ].clockCycles.append(cycle)

			block = (currLine // 8) % 2
			word = currLine % 8
			# print("OKKKKKKKKK " + str(self.instructionMemory[block][word].lineNum))
			self.pipeline["IF"] = deepcopy(self.instructionMemory[block][word])
			# self.pipeline["IF"].proc_done = 0
			currLine += 1
			self.iCache_numAccesses += 1
			# self.theCommands[ self.pipeline["IF"].lineNum ].clockCycles.append(cycle)
		# print("if_ctrl!" + str(cycle))
		return currLine


	def pipelineControllerID(self, currLine, cycle):
		# sys.exit()
		if (self.pipelineShift("ID")):
			# print("id_ctrl!" + str(cycle))
			self.decode(self.pipeline["ID"])
			# cycle -= 1
			# self.pipelineClockCycles[self.pipeline["ID"].lineNum-1] += str(cycle) + "\t"
			self.theCommands[ self.pipeline["ID"].lineNum-1 ].clockCycles.append(cycle-1)

			# print(self.pipeline["ID"].instruction)
			if (self.pipeline["ID"].instruction == "J"):
				for command in self.theCommands:
					# print(command.label)
					if ((command.label != "") and (command.label == self.pipeline["ID"].operands[0])):
						# print(command.lineNum)
						# sys.exit()
						return True, command.lineNum-1
				print("Got error in jumping to label \"" + self.pipeline["ID"].label + "\" -- label not found")
				print("....Now terminating the program")
				sys.exit()
			elif (self.pipeline["ID"].instruction == "BEQ"):
				# print("WENT HERE!")
				regNum1 = int(self.pipeline["ID"].operands[0][1:])
				regNum2 = int(self.pipeline["ID"].operands[1][1:])
				if (self.registers[regNum1] == self.registers[regNum2]):
					# print(self.pipeline["ID"].operands[2])
					for command in self.theCommands:
						# print(command.label)
						if ((command.label != "") and (command.label == self.pipeline["ID"].operands[2])):
							# print(command.lineNum)
							# sys.exit()
							return True, command.lineNum-1
					print("Got error in branching to label \"" + self.pipeline["ID"].label + "\" -- label not found")
					print("....Now terminating the program")
					sys.exit()
			elif (self.pipeline["ID"].instruction == "BNE"):
				regNum1 = int(self.pipeline["ID"].operands[0][1:])
				regNum2 = int(self.pipeline["ID"].operands[1][1:])
				if (self.registers[regNum1] != self.registers[regNum2]):
					# print(self.pipeline["ID"].operands[2])
					for command in self.theCommands:
						# print(command.label)
						if ((command.label != "") and (command.label == self.pipeline["ID"].operands[2])):
							# print(command.lineNum)
							# sys.exit()
							return True, command.lineNum-1
					print("Got error in branching to label \"" + self.pipeline["ID"].label + "\" -- label not found")
					print("....Now terminating the program")
					sys.exit()
			elif (self.pipeline["ID"].instruction == "LI"):
				regNum = int(self.pipeline["ID"].operands[0][1:])
				# print(self.pipeline["ID"].operands[1])
				immVal = int(self.pipeline["ID"].operands[1])
				self.registers[regNum] = immVal
				# sys.exit()
		return False, currLine
				
	

	def pipelineControllerEX1(self, cycle):
		if (self.pipelineShift("EX1")):
			# print("ex1_ctrl!" + str(cycle))
			# cycle -= 1
			# self.pipelineClockCycles[self.pipeline["EX1"].lineNum-1] += str(cycle) + "\t"
			self.theCommands[ self.pipeline["EX1"].lineNum-1 ].clockCycles.append(cycle-1)

			if (self.pipeline["EX1"].instruction == "AND"):
				regNum1 = int(self.pipeline["EX1"].operands[0][1:])
				regNum2 = int(self.pipeline["EX1"].operands[1][1:])
				regNum3 = int(self.pipeline["EX1"].operands[2][1:])
				self.registers[regNum1] = self.registers[regNum2] & self.registers[regNum3]
				# sys.exit()
			elif (self.pipeline["EX1"].instruction == "ANDI"):
				regNum1 = int(self.pipeline["EX1"].operands[0][1:])
				regNum2 = int(self.pipeline["EX1"].operands[1][1:])
				immVal = int(self.pipeline["EX1"].operands[2])
				self.registers[regNum1] = self.registers[regNum2] & immVal
			elif (self.pipeline["EX1"].instruction == "OR"):
				regNum1 = int(self.pipeline["EX1"].operands[0][1:])
				regNum2 = int(self.pipeline["EX1"].operands[1][1:])
				regNum3 = int(self.pipeline["EX1"].operands[2][1:])
				self.registers[regNum1] = self.registers[regNum2] | self.registers[regNum3]
			elif (self.pipeline["EX1"].instruction == "ORI"):
				regNum1 = int(self.pipeline["EX1"].operands[0][1:])
				regNum2 = int(self.pipeline["EX1"].operands[1][1:])
				immVal = int(self.pipeline["EX1"].operands[2])
				self.registers[regNum1] = self.registers[regNum2] | immVal
			elif (self.pipeline["EX1"].instruction == "LW"):
				regNum1 = int(self.pipeline["EX1"].operands[0][1:])
				offset = int(self.pipeline["EX1"].operands[1])
				regNum2 = int(self.pipeline["EX1"].operands[2][1:])
				# print(offset, regNum2)
				self.dCache_numAccesses += 1
				if ( (offset + self.registers[regNum2] <= 0) and (offset + self.registers[regNum2] >= len(self.registers)) ):
					self.registers[regNum1] = dataMemory[offset + self.registers[regNum2]]
				else:
					self.dCache_numMisses += 1
				# sys.exit()
			elif (self.pipeline["EX1"].instruction == "SW"):
				regNum1 = int(self.pipeline["EX1"].operands[0][1:])
				offset = int(self.pipeline["EX1"].operands[1])
				regNum2 = int(self.pipeline["EX1"].operands[2][1:])
				# print(offset, regNum2)
				self.dCache_numAccesses += 1
				if ( (offset + self.registers[regNum2] <= 0) and (offset + self.registers[regNum2] >= len(self.registers)) ):
					dataMemory[offset + self.registers[regNum2]] = self.registers[regNum1]
				else:
					self.dCache_numMisses += 1
				# sys.exit()


	def pipelineControllerEX2(self, cycle):
		if (self.pipelineShift("EX2")):
			# print("ex2_ctrl!" + str(cycle))
			if (self.pipeline["EX2"].instruction == "ADD"):
				regNum1 = int(self.pipeline["EX2"].operands[0][1:])
				regNum2 = int(self.pipeline["EX2"].operands[1][1:])
				regNum3 = int(self.pipeline["EX2"].operands[2][1:])
				self.registers[regNum1] = self.registers[regNum2] + self.registers[regNum3]
				# sys.exit()
			elif (self.pipeline["EX2"].instruction == "ADDI"):
				regNum1 = int(self.pipeline["EX2"].operands[0][1:])
				regNum2 = int(self.pipeline["EX2"].operands[1][1:])
				immVal = int(self.pipeline["EX2"].operands[2])
				self.registers[regNum1] = self.registers[regNum2] + immVal
			elif (self.pipeline["EX2"].instruction == "SUB"):
				regNum1 = int(self.pipeline["EX2"].operands[0][1:])
				regNum2 = int(self.pipeline["EX2"].operands[1][1:])
				regNum3 = int(self.pipeline["EX2"].operands[2][1:])
				self.registers[regNum1] = self.registers[regNum2] - self.registers[regNum3]
				# sys.exit()
			elif (self.pipeline["EX2"].instruction == "SUBI"):
				regNum1 = int(self.pipeline["EX2"].operands[0][1:])
				regNum2 = int(self.pipeline["EX2"].operands[1][1:])
				immVal = int(self.pipeline["EX2"].operands[2])
				self.registers[regNum1] = self.registers[regNum2] - immVal


	def pipelineControllerEX3(self, cycle):
		if (self.pipelineShift("EX3")):
			# print("ex3_ctrl!" + str(cycle))
			# if( (self.pipeline["EX3"].instruction == "ADDI") or (self.pipeline["EX3"].instruction == "ADD") ):
			# 	print(self.pipeline["EX3"].instruction + " " + str(cycle-1))# + "\n")
			if (self.pipeline["EX3"].instruction == "MULT"):
				regNum1 = int(self.pipeline["EX3"].operands[0][1:])
				regNum2 = int(self.pipeline["EX3"].operands[1][1:])
				regNum3 = int(self.pipeline["EX3"].operands[2][1:])
				self.registers[regNum1] = self.registers[regNum2] * self.registers[regNum3]
				# sys.exit()
			elif (self.pipeline["EX3"].instruction == "MULTI"):
				regNum1 = int(self.pipeline["EX3"].operands[0][1:])
				regNum2 = int(self.pipeline["EX3"].operands[1][1:])
				immVal = int(self.pipeline["EX3"].operands[2])
				self.registers[regNum1] = self.registers[regNum2] * immVal


	def pipelineControllerMEM(self, cycle):
		if (self.pipelineShift("MEM")):
			# print("mem_ctrl!" + str(cycle))
			# if( (self.pipeline["MEM"].instruction == "MULT") or (self.pipeline["MEM"].instruction == "MULTI") ):
				# print(self.pipeline["MEM"].instruction + " " + str(cycle-1))# + "\n")
			# cycle -= 1
			# self.pipelineClockCycles[self.pipeline["MEM"].lineNum-1] += str(cycle) + "\t"
			self.theCommands[ self.pipeline["MEM"].lineNum-1 ].clockCycles.append(cycle-1)



	def pipelineControllerWB(self, cycle):
		if (self.pipelineShift("WB")):
			# print("wb_ctrl!" + str(cycle))
			# if( (self.pipeline["WB"].instruction == "LW") or (self.pipeline["WB"].instruction == "SW") ):
				# print(self.pipeline["WB"].instruction + " " + str(cycle-1))# + "\n")	
			# cycle -= 1
			# self.pipelineClockCycles[self.pipeline["WB"].lineNum-1] += str(cycle) + "\t"
			self.theCommands[ self.pipeline["WB"].lineNum-1 ].clockCycles.append(cycle-1)



	def clearController(self, cycle):
		# print("HERE 2.5!")
		if(self.pipeline["WB"].lineNum != 0):
			# print("clear_ctrl!" + str(cycle))
			# cycle -= 1
			# self.pipelineClockCycles[self.pipeline["WB"].lineNum-1] += str(cycle) + "\t"
			self.theCommands[ self.pipeline["WB"].lineNum-1 ].clockCycles.append(cycle-1)
			self.pipeline["WB"].lineNum = 0


	def registerEmpty(self):
		result = 0
		for stage in self.pipelineStages:
			# print("registerEmpty!")
			if (self.pipeline[stage].lineNum != 0):
				result += 1
		return result
