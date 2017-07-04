import sys
from copy import deepcopy

class theSimulator:
	"""docstring for theSimulator"""
	def __init__(self, instructionFileName, dataFileName):
		self.cmd_lines = [ Instruction() for i in range(32) ]
		self.num_line = 0
		self.registers = [ 0 for i in range(32) ]
		self.clock_cycles = [ "" for i in range(32) ]
		self.reg_buff = [ Instruction() for i in range(7)] #0=if 1=id 2=ex1 3=ex2 4=ex3 5=mem 6=wb
		self.memory_data = [ Instruction() for i in range(32) ]
		self.i_memory = [ [ Instruction() for i in range(8) ] for i in range(2) ]
		self.d_memory = [ [ "" for i in range(4) ] for i in range(4) ]
		self.i_cache_acess = 0
		self.i_cache_misses = 0
		self.d_cache_acess = 0
		self.d_cache_misses = 0

		self.parse_instructions(instructionFileName)
		self.populateData(dataFileName)
		self.run()
		self.print_code()
		

	def parse_instructions(self, fileName):
		self.num_line = 0
		rawLines = []
		with open(fileName) as FILE:
			rawLines = FILE.readlines()
		
		# print("HET!")
		# print(len(rawLines))
		
		for line in range(len(rawLines)):
			# print(line)
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
						self.cmd_lines[self.num_line].header = token
						token = ""
					elif( (not inst_token) and ((i+1 >= len(rawLines[line]) or (rawLines[line][i+1] == ' ') or \
						(rawLines[line][i+1] == '\t')))):# or (rawLines[line][i+1] == 00))):
						# print("HERE 2")
						# print(self.num_line)
						# print(self.num_line)
						self.cmd_lines[self.num_line].instruction = token
						self.cmd_lines[self.num_line].line_numb = self.num_line
						inst_token = 1
						token = ""
						self.num_line += 1
						self.cmd_lines[self.num_line-1].line_numb = self.num_line
					elif( (inst_token) and (rawLines[line][i] != 00) ):
						# print("HERE 3")
						self.cmd_lines[self.num_line-1].operation = rawLines[line][i:len(rawLines[line])-1]
						# print("OP " + self.cmd_lines[self.num_line-1].operation)
						i = len(rawLines[line]) - 1
						inst_token = 0
					# else:
					# 	try:
							
					# 	except IndexError:
					# 		continue
				i += 1


	def populateData(self, fileName):
		with open(fileName) as FILE:
			self.theData = FILE.readlines()


	def print_code(self):
		runningString = "Line #" + "\t" + "Label" + "\t" + "Operation" + "\t\tIF\tID\tEX\tMEM\tWB\n"
		for i in range(self.num_line):
			runningString += str(self.cmd_lines[i].line_numb)
			if (self.cmd_lines[i].header == ""):
				runningString += "\t\t"
			else:
				runningString += "\t" + str(self.cmd_lines[i].header) + "\t"
			runningString += self.cmd_lines[i].instruction + "\t"
			if (self.cmd_lines[i].instruction == "HLT"):
				runningString += "\t\t"
			else:
				runningString += str(self.cmd_lines[i].operation) + "   \t"
			runningString += self.clock_cycles[i] + "\n"
		
		# print(type(self.clock_cycles[i]))
		runningString += "\n\nTotal number of access requests for instruction cache: " \
			+ str(self.i_cache_acess) + "\n" \
			+ "Number of instruction cache hits: " \
			+ str(self.i_cache_acess - self.i_cache_misses) + "\n\n" \
			+ "Total number of access requests for data cache: " \
			+ str(self.d_cache_acess) + "\n" \
			+ "Number of data cache hits: " \
			+ str(self.d_cache_acess - self.d_cache_misses) + "\n\n"

		print(runningString)


	def run(self):
		pc = 0
		cycle = 0
		pop_cycles = -1
		counter = 0
		while( (pc == 0) or (self.isDone()) ):
			# print("HERE 1!")
			cycle += 1
			print("pop_cy" + str(pop_cycles))
			if( (not self.got_instruction(pc)) and (pop_cycles < 0) ):
				print("I CRAZILY WENT HERE!")
				pop_cycles = 23
				# print("HERE 2!")
			print("pop_cy" + str(pop_cycles))
			self.clear_control(cycle)
			self.wb_control(cycle)
			self.mem_control(cycle)
			self.ex3_control(cycle)
			self.ex2_control(cycle)
			self.ex1_control(cycle)
			self.id_control(cycle)
			pc = self.if_control(pc, cycle)
			if (pop_cycles == 0):
				print("I WENT HERE!")
				self.pop_instruction_cache(pc, cycle)
				pop_cycles -= 1
				# counter += 1
			elif (pop_cycles > 0):
				pop_cycles -= 1
			# counter += 1
			# counter += 1
			# if (counter == 2):
			# 	sys.exit()
		self.reg_buff[0].line_numb=0
		self.reg_buff[1].line_numb=0
		self.reg_buff[2].line_numb=0
		while ( self.reg_empty() ):
			cycle += 1
			self.clear_control(cycle)
			self.wb_control(cycle)
			self.mem_control(cycle)
			self.ex3_control(cycle)
			self.ex2_control(cycle)
			self.ex1_control(cycle)


	def isDone(self):
		print("isDone!")
		result = 0
		if (self.reg_buff[2].instruction != "HLT"):
			result = 1
		# print(self.reg_buff[2].instruction == "HLT")
		# sys.exit()
		print(result)
		return result


	def got_instruction(self, pc):
		print("got_instruction!" + str(pc))
		block = (pc // 8) % 2
		word = pc % 8
		print(block, word)
		print(self.i_memory[block][word].line_numb)
		print(self.cmd_lines[pc].line_numb)
		if (self.i_memory[block][word].line_numb == self.cmd_lines[pc].line_numb):
			return 1
		else:
			return 0


	def pop_instruction_cache(self, pc, cycle):
		print("pop_instruction_cache!" + str(cycle) + " " + str(pc))
		block = (pc // 8) % 2
		word = (pc // 8) * 8
		print(block, word)
		self.i_cache_misses += 1
		print("Populating instructions " + str(cycle))
		for i in range(8):
			print(self.cmd_lines[word+i].line_numb)
			self.i_memory[block][i] = self.cmd_lines[word+i]
		# sys.exit()
		return cycle


	def buff_move(self, pos):
		print("buff_move!" + str(pos))
		print("B4 -- self.reg_buff[pos].line_numb\t" + str(self.reg_buff[pos].line_numb))
		print("B4 -- self.reg_buff[pos-1].line_numb\t" + str(self.reg_buff[pos-1].line_numb))
		if ( (self.reg_buff[pos].line_numb == 00) and (self.reg_buff[pos-1].line_numb != 00) ):
			print("THIS IS SET!")
			self.reg_buff[pos] = deepcopy(self.reg_buff[pos-1])
			self.reg_buff[pos-1].line_numb = 0
			# print("self.reg_buff[pos].line_numb\t" + str(self.reg_buff[pos].line_numb))
			# print("self.reg_buff[pos-1].line_numb\t" + str(self.reg_buff[pos-1].line_numb))
			return 1
		return 0


	def decode(self, line):
		print("decode!" + str(line))
		if (line.instruction == "LI"):
			line.ops[0]=line.operation[0:3]
			line.ops[3]=line.operation[4:]
			print(line.instruction + " " + line.ops[0] + " " + line.ops[3] )#+ "\n")
		elif ( (line.instruction == "ADDI") or (line.instruction == "SUBI") or (line.instruction == "ANDI") \
			or (line.instruction == "ORI") or (line.instruction == "BEQ") or (line.instruction == "BNE") or (line.instruction == "MULTI") ):
			line.ops[0] = line.operation[0:3]
			line.ops[1] = line.operation[4:7]
			line.ops[3] = line.operation[8:]
			print(line.instruction + " " + line.ops[0] + " " + line.ops[1] + " " + line.ops[3])# + "\n")
		elif ( (line.instruction == "LW") or (line.instruction == "SW")):
			line.ops[0] = line.operation[0:3]
			temp = line.operation.index("(")
			line.ops[3] = line.operation[4:temp+1]
			line.ops[1] = line.operation[temp+1:temp+3]
			print(line.instruction + " " + line.ops[0] + " " + line.ops[3] + " " + line.ops[1])# + "\n")
		elif( (line.instruction == "ADD") or (line.instruction == "SUB") or (line.instruction == "OR") \
			or (line.instruction == "AND") or (line.instruction == "MULT")):
			line.ops[0] = line.operation[0:3]
			line.ops[1] = line.operation[4:7]
			line.ops[2] = line.operation[8:]
			print(line.instruction + " " + line.ops[0] + " " + line.ops[1] + " " + line.ops[2])# + "\n")
		elif(line.instruction=="J"):
			line.ops[4] = line.operation
			print(line.instruction + " " + line.ops[4])# + "\n")


	def if_control(self, pc, cycle):
		block= (pc // 8)%2
		word= pc%8
		if( (self.reg_buff[0].line_numb == 00) and (self.i_memory[block][word].line_numb == (pc+1)) ):
			block = (pc//8)%2
			word = pc%8
			print("OKKKKKKKKK " + str(self.i_memory[block][word].line_numb))
			self.reg_buff[0] = deepcopy(self.i_memory[block][word])
			self.reg_buff[0].proc_done = 0
			pc += 1
			self.i_cache_acess += 1
		print("if_ctrl!" + str(cycle))
		return pc


	def id_control(self, cycle):
		if(self.buff_move(1)):
			print("id_ctrl!" + str(cycle))
			self.decode(self.reg_buff[1])
			cycle -= 1
			self.clock_cycles[self.reg_buff[1].line_numb-1] += str(cycle) + "\t"
	

	def ex1_control(self, cycle):
		if(self.buff_move(2)):
			print("ex1_ctrl!" + str(cycle))
			cycle -= 1
			self.clock_cycles[self.reg_buff[2].line_numb-1] += str(cycle) + "\t"


	def ex2_control(self, cycle):
		if(self.buff_move(3)):
			print("ex2_ctrl!" + str(cycle))


	def ex3_control(self, cycle):
		if(self.buff_move(4)):
			print("ex3_ctrl!" + str(cycle))
			if( (self.reg_buff[4].instruction == "ADDI") or (self.reg_buff[4].instruction == "ADD") ):
				print(self.reg_buff[4].instruction + " " + str(cycle-1))# + "\n")


	def mem_control(self, cycle):
		if(self.buff_move(5)):
			print("mem_ctrl!" + str(cycle))
			if( (self.reg_buff[5].instruction == "MULT") or (self.reg_buff[5].instruction == "MULTI") ):
				print(self.reg_buff[5].instruction + " " + str(cycle-1))# + "\n")
			cycle -= 1
			self.clock_cycles[self.reg_buff[5].line_numb-1] += str(cycle) + "\t"


	def wb_control(self, cycle):
		if(self.buff_move(6)):
			print("wb_ctrl!" + str(cycle))
			if( (self.reg_buff[6].instruction == "LW") or (self.reg_buff[6].instruction == "SW") ):
				print(self.reg_buff[6].instruction + " " + str(cycle-1))# + "\n")	
			cycle -= 1
			self.clock_cycles[self.reg_buff[6].line_numb-1] += str(cycle) + "\t"


	def clear_control(self, cycle):
		# print("HERE 2.5!")
		if(self.reg_buff[6].line_numb != 00):
			print("clear_ctrl!" + str(cycle))
			cycle-= 1
			self.clock_cycles[self.reg_buff[6].line_numb-1] += str(cycle) + "\t"
			self.reg_buff[6].line_numb = 00


	def reg_empty(self):
		result = 0
		for i in range(len((self.reg_buff))):
			print("reg_empty!")
			if (self.reg_buff[i].line_numb != 0):
				result += 1
		return result


class Instruction:
	"""docstring"""
	def __init__(self):
		self.header = ""
		self.instruction = ""
		self.operation = ""
		self.line_numb = 0
		self.ops = [ "" for i in range(5) ]
		self.proc_done = 0
