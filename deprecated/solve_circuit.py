import numpy as np

R1 = 25
C = 2
R2 = 10
P = 3

Qin = 2
Pd = 30
inf = np.inf

circtest = ['R',['C'],['C'],'R',['C','G'],'L',['C','R','G'],[['C'],['R']]]

circuit = ['R',['C','G'],'R']
values  = [ R1, [ C ], R2 ]

circuitTem = ['R',[['C'],['R']]]
valuesTem  = [ R1,[[ C ],[ R2 ]]]

circuitCoro = ['R',['C','G'],'R',['C','P','G'],'R']
valuesCoro = [R1,[C],R1,[C,P],R2]

circuitCoroTem = ['R',[['C'],['R',[['C','P'],['R']]]]]
valuesCoroTem = [R1,[[C],[R1,[[C,P],[R2]]]]]

t = np.arange(100)
P1 = np.zeros_like(t)+4
P2 = np.zeros_like(t)+2
Dt = t[1]-t[0]
n = 10

# def nb_inc(circuit) :
# 	pres = 1		# Base flow and pressure in the wire
# 	flow = 1
# 	for elem in circuit :
# 		if elem == 'R' or elem == 'C' or elem == 'P' :
# 			pres += 1				# New pressure in the system
# 		elif elem == 'G' :
# 			pres -= 1				# Previous pressure is actually ground
# 		elif isinstance(elem,list) :
# 			if isinstance(elem[0],list) :
# 				pres += 1				# 
# 				flow += 2				# Pressure at intersection and two flows
# 				for el in elem :
# 					t1, t2 = nb_inc(el)
# 					pres += t1 - 2		# Add one pressure only if more than one element
# 					flow += t2 - 1		# and remove entry flow and pressure
# 			else :
# 				flow += 2       
# 				t1, t2 = nb_inc(elem)
# 				pres += t1 - 1		# 
# 				flow += t2 - 1		# Remove entry flow and pressure
# 	return pres, flow

class Circuit:
	def __init__(self, circuit, values):
		self.circuit = circuit
		self.values = values
		self.nbP, self.nbQ = self.nb_inc(circuit)
		self.globidxQ = self.nbP
		self.Amat = np.zeros((self.nbP+self.nbQ,self.nbP+self.nbQ))
		self.Bvec = np.zeros((self.nbP+self.nbQ))
		self.line = 0

	def nb_inc(self, circuit) :
		pres = 1		# Base flow and pressure in the wire
		flow = 1
		for elem in circuit :
			if elem == 'R' or elem == 'C' or elem == 'P' :
				pres += 1				# New pressure in the system
			elif elem == 'G' :
				pres -= 1				# Previous pressure is actually ground
			elif isinstance(elem,list) :
				if isinstance(elem[0],list) :
					pres += 1				# 
					flow += 2				# Pressure at intersection and two flows
					for el in elem :
						t1, t2 = self.nb_inc(el)
						pres += t1 - 2		# Add one pressure only if more than one element
						flow += t2 - 1		# and remove entry flow and pressure
				else :
					flow += 2       
					t1, t2 = self.nb_inc(elem)
					pres += t1 - 1		# 
					flow += t2 - 1		# Remove entry flow and pressure
		return pres, flow

	def build_Amat(self, circuit, values, idxP1=0, idxP2=1, idxPout=-1) :
		'''
		circuit : list of components defined by their type in one letter
		values : same architecture as circuit, but with values corresponding to each element
		Amat : mass matrix
		Bvec : b vector of the system
		'''

		idxQ = self.globidxQ

		if len(circuit)==0 :
			return

		if self.line == 0 :
			idxPout = self.nb_inc(circuit)[0]-1

		for i in range(len(circuit)):
			elem = circuit[i]

			if i == len(circuit)-1 and not isinstance(circuit[-1],list) :
				idxP2 = idxPout
				
			if elem == 'R' :                      # P1 - P2 = RQ
				self.Amat[self.line,idxQ] 	+= -values[i]
				self.Amat[self.line,idxP1] 	+= 1
				self.Amat[self.line,idxP2] 	+= -1

				idxP1 = idxP2
				idxP2 += 1
				self.line += 1

			elif elem == 'C' :                    # Q = Cd(P1-P2) = CdP1 - CdP2
				self.Amat[self.line,idxQ] 	+= 1
				self.Amat[self.line,idxP1] 	+= -values[i]/Dt
				self.Bvec[self.line] 		+= -values[i]*P1[n]/Dt
				self.Amat[self.line,idxP2] 	+= values[i]/Dt
				self.Bvec[self.line] 		+= values[i]*P2[n]/Dt
				
				idxP1 = idxP2
				idxP2 += 1
				self.line += 1

			elif elem == 'P' :                    # P1 - P2 = P
				self.Amat[self.line,idxP1] 	+= 1
				self.Amat[self.line,idxP2] 	+= -1
				self.Bvec[self.line] 		+= values[i]
				
				idxP1 = idxP2
				idxP2 += 1
				self.line += 1

			elif elem == 'G' :                    # P1 - P2 = P
				self.Amat[self.line-1,idxP1] = 0
			
			elif isinstance(elem,list) :
				if isinstance(elem[0],list) :
					Qline = self.line
					self.Amat[Qline,idxQ] += 1
					self.line += 1

					lengthP = self.nb_inc([elem])[0] - 1

					idxP2_shift = 0
					for j in range(len(elem)) :
						self.globidxQ += 1
						self.Amat[Qline,self.globidxQ] += -1
						self.build_Amat(circuit[i][j], values[i][j], idxP1, idxP2+idxP2_shift, idxP1+lengthP)
						idxP2_shift += self.nb_inc(elem[j])[0] - 2
					
					idxP1 += lengthP
					idxP2 = idxP1+1
					
				else :
					Qline = self.line
					self.Amat[Qline,idxQ] += 1
					self.line += 1

					lengthP = self.nb_inc(elem)[0] - 1

					self.globidxQ += 1
					self.Amat[Qline,self.globidxQ] += -1
					self.build_Amat(circuit[i], values[i], idxP1, idxP2, idxP1+lengthP)
					
					self.globidxQ += 1
					self.Amat[Qline,self.globidxQ] += -1
					idxQ = self.globidxQ
					
					idxP2 = idxP1 + lengthP + 1

		return 0
	
	def print_Amat(self) :
		self.build_Amat(self.circuit,self.values)
		return self.Amat

	##########################
	### Printing functions ###
	##########################

	def recursive_len(self, item):
		if isinstance(item,list):
			return sum(self.recursive_len(subitem) for subitem in item)
		else:
			return 1
		
	def max_circ_len(self, circ):
		circlen = 0
		for i in range(len(circ)) :
			if isinstance(circ[i],list) :
				if isinstance(circ[i][0],list) :
					sublen = 0
					for el in circ[i] :
						temp = self.max_circ_len(el)
						sublen = max([temp,sublen])
					circlen += sublen
				else :
					circlen += max([self.max_circ_len(circ[i]),self.max_circ_len(circ[i+1:])])
					return circlen
			else :
				circlen += 1
		return circlen
	
	def circ_dep(self, circ):
		circdep = np.array([0 for i in range(self.max_circ_len(circ))])
		cpcirc = circ.copy()
		for elem in circ :
			if isinstance(elem,list) and not isinstance(elem[0],list) :
				cpcirc.remove(elem)
		pos = self.max_circ_len(cpcirc)
		for i in range(len(circ)-1,-1,-1) :
			elem = circ[i]
			if isinstance(elem,list) :
				if isinstance(elem[0],list) :
					leng = self.max_circ_len(elem)
					pos -= leng
					for el in elem :
						circdep[pos:pos+leng] += self.circ_dep(el)
				else :
					leng = self.max_circ_len(elem)
					circdep[pos:pos+leng] += 1
					circdep[pos:pos+leng] = np.max(circdep[pos:pos+leng])
			else :
				pos -= 1
				circdep[pos] += 1
		return circdep

	def max_circ_dep(self, circ):
		return max(self.circ_dep(circ))

	def make_list_str(self, circ, leng = 0, noend = False):
		if leng == 0 :
			list_char = np.array([['      ' for _ in range(self.max_circ_len(circ)+1)] for __ in range(self.max_circ_dep(circ))])
		else :
			list_char = np.array([['      ' for _ in range(leng)] for __ in range(self.max_circ_dep(circ))])
		
		col = 0

		for i in range(len(circ)) :
			elem = circ[i]
			if isinstance(elem,list) :
				if isinstance(elem[0],list) :
					offset = 0
					maxlen = 0
					for el in elem :
						maxlen = max(maxlen,self.max_circ_len(el))
					for el in elem :
						dep = self.max_circ_dep(el)
						list_char[offset:offset+dep,col:col+maxlen+1] = self.make_list_str(el,maxlen+1)
						offset += dep
					col += maxlen
					regroup = True
				else :
					maxlen = self.max_circ_len(elem)
					offset = np.max(self.circ_dep(circ[i+1:])[:maxlen])
					dep = self.max_circ_dep(elem)
					list_char[offset:offset+dep,col:col+maxlen+1] = self.make_list_str(elem,maxlen+1,True)
					for i in range(1,offset):
						list_char[i,col] = '┼     '
					regroup = True
			else :
				if i == 0 or regroup :
					list_char[0,col] = '┼──'
					regroup = False
				else :
					list_char[0,col] = '───'

				if elem == 'G' :
					list_char[0,col] += '⏚'
				else :
					list_char[0,col] += elem
				if noend and i == len(circ)-1 :
					list_char[0,col] += '   '
				else :
					list_char[0,col] += '───'
				col += 1
				
		for i in range(len(list_char[0])):
			if i == (len(list_char[0])-1) :
				list_char[0,i] = '┼     '
				if noend :
					list_char[0,i] = '      '
					noend = False
			elif list_char[0,i] == '      ' :
				list_char[0,i] = '──────'
			elif list_char[0,i] == '┼     ' :
				list_char[0,i] = '┼─────'

		return list_char

	def correct_str(self,circ_str):
		list_str = circ_str.split('\n')[:-1]
		for i in range(len(list_str)) :
			list_str[i] = [*list_str[i]]
		list_str = np.array(list_str)
		def pad_with(vector, pad_width, iaxis, kwargs):
			pad_value = kwargs.get('padder', ' ')
			vector[:pad_width[0]] = pad_value
			vector[-pad_width[1]:] = pad_value
		list_str = np.pad(list_str, 1, pad_with)
		correction = np.zeros_like(list_str)
		for i in range(len(list_str)) :
			for j in range(len(list_str[0])) :
				if list_str[i,j] == '┼' :
					if list_str[i+1,j] != '┼' and list_str[i-1,j] != '┼' :
						correction[i,j] = '─'
					if list_str[i+1,j] == '┼' and list_str[i-1,j] == '┼' and list_str[i,j+1] == ' ' and list_str[i,j-1] == ' ' :
						correction[i,j] = '│'
					if list_str[i+1,j] == '┼' and list_str[i-1,j] == '┼' and list_str[i,j+1] != ' ' and list_str[i,j-1] == ' ' :
						correction[i,j] = '├'
					if list_str[i+1,j] == '┼' and list_str[i-1,j] == '┼' and list_str[i,j+1] == ' ' and list_str[i,j-1] != ' ' :
						correction[i,j] = '┤'
					if list_str[i+1,j] == '┼' and list_str[i-1,j] != '┼' and list_str[i,j+1] != ' ' and list_str[i,j-1] != ' ' :
						correction[i,j] = '┬'
					# if list_str[i+1,j] == '┼' and list_str[i-1,j] != '┼' and list_str[i,j+1] == ' ' and list_str[i,j-1] != ' ' :
					#     correction[i,j] = '┐'
					if list_str[i+1,j] == '┼' and list_str[i-1,j] != '┼' and list_str[i,j+1] != ' ' and list_str[i,j-1] == ' ' :
						correction[i,j] = '┌'
					if list_str[i+1,j] != '┼' and list_str[i-1,j] == '┼' and list_str[i,j+1] != ' ' and list_str[i,j-1] != ' ' :
						correction[i,j] = '┴'
					if list_str[i+1,j] != '┼' and list_str[i-1,j] == '┼' and list_str[i,j+1] == ' ' and list_str[i,j-1] != ' ' :
						correction[i,j] = '┘'
					if list_str[i+1,j] != '┼' and list_str[i-1,j] == '┼' and list_str[i,j+1] != ' ' and list_str[i,j-1] == ' ' :
						correction[i,j] = '└'
					if list_str[i+1,j] == '┼' and list_str[i-1,j] != '┼' and list_str[i,j+1] == ' ' and list_str[i,j-1] != ' ' :
						correction[i,j] = '┬'


		for i in range(len(list_str)) :
			for j in range(len(list_str[0])) :
				if list_str[i,j] == '┼' and correction[i,j] != '' :
					list_str[i,j] = correction[i,j]
		
		list_str = list_str[1:-1,1:-1]
		circ_str = ''
		for i in range(len(list_str)) :
			for j in range(len(list_str[0])) :
				circ_str += list_str[i,j]
			circ_str += '\n'

		return circ_str

	def make_str(self,circ):
		list_char = self.make_list_str(circ)
		circ_str = ''
		for i in range(len(list_char)) :
			for j in range(len(list_char[0])) :
				circ_str += list_char[i,j]
			circ_str = circ_str[:-5] + '\n'
		circ_str = self.correct_str(circ_str)
		return circ_str

	def __str__(self):
		return self.make_str(self.circuit)

# build_Amat(circuitCoro,valuesCoro)
# build_Amat(circuit,values)
# build_Amat(circuitCoroTem,valuesCoroTem)
# init_cond(Qin,Pd)
# print(Amat)
# print(Bvec)

RCR = Circuit(circuit,values)
RCRTem = Circuit(circuitTem,valuesTem)
print(RCR.print_Amat())
print(RCRTem.print_Amat())
Coro = Circuit(circuitCoro,valuesCoro)
CoroTem = Circuit(circuitCoroTem,valuesCoroTem)
test = Circuit(circtest,circtest)
# print(RCR)
# print(Coro)
# print(CoroTem)
# print(test)
# print(nb_inc(circuitCoro))
# print(nb_inc(circuitCoroTem))

# ⏚
# ┼ ┤ ├ ┬ ┴ ┌ ┐ └ ┘ │
# ┨ ┠