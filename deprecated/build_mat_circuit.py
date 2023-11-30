import numpy as np

R1 = 25
C = 2
R2 = 10
P = 3

Qin = 2
Pd = 10
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

def nb_inc(circuit) :
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
					t1, t2 = nb_inc(el)
					pres += t1 - 2		# Add one pressure only if more than one element
					flow += t2 - 1		# and remove entry flow and pressure
			else :
				flow += 2       
				t1, t2 = nb_inc(elem)
				pres += t1 - 1		# 
				flow += t2 - 1		# Remove entry flow and pressure
	return pres, flow

nbP, nbQ = nb_inc(circuit)
globidxQ = nbP
Amat = np.zeros((nbP+nbQ,nbP+nbQ))
Bvec = np.zeros((nbP+nbQ))
line = 0

def build_Amat(circuit,values,idxP1=0,idxP2=1,idxPout=-1) :
	'''
	circuit : list of components defined by their type in one letter
	values : same architecture as circuit, but with values corresponding to each element
	Amat : mass matrix
	Bvec : b vector of the system
	'''

	global Amat
	# global Bvec
	global line
	global globidxQ
	idxQ = globidxQ

	if len(circuit)==0 :
		return

	if line == 0 :
		idxPout = nb_inc(circuit)[0]-1

	for i in range(len(circuit)):
		elem = circuit[i]

		if i == len(circuit)-1 and not isinstance(circuit[-1],list) :
			idxP2 = idxPout
			
		if elem == 'R' :                      # P1 - P2 = RQ
			Amat[line,idxQ] += -values[i]
			Amat[line,idxP1] += 1
			Amat[line,idxP2] += -1

			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'C' :                    # Q = Cd(P1-P2) = CdP1 - CdP2
			Amat[line,idxQ] += 1
			Amat[line,idxP1] += -values[i]/Dt
			Bvec[line] += -values[i]*P1[n]/Dt
			Amat[line,idxP2] += values[i]/Dt
			Bvec[line] += values[i]*P2[n]/Dt
			
			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'P' :                    # P1 - P2 = P
			Amat[line,idxP1] += 1
			Amat[line,idxP2] += -1
			Bvec[line] += values[i]
			
			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'G' :                    # P1 - P2 = P
			Amat[line-1,idxP1] = 0
		
		elif isinstance(elem,list) :
			if isinstance(elem[0],list) :
				Qline = line
				Amat[Qline,idxQ] += 1
				line += 1

				lengthP = nb_inc([elem])[0] - 1

				idxP2_shift = 0
				for j in range(len(elem)) :
					globidxQ += 1
					Amat[Qline,globidxQ] += -1
					build_Amat(circuit[i][j], values[i][j], idxP1, idxP2+idxP2_shift, idxP1+lengthP)
					idxP2_shift += nb_inc(elem[j])[0] - 2
				
				idxP1 += lengthP
				idxP2 = idxP1+1
				
			else :
				Qline = line
				Amat[Qline,idxQ] += 1
				line += 1

				lengthP = nb_inc(elem)[0] - 1

				globidxQ += 1
				Amat[Qline,globidxQ] += -1
				build_Amat(circuit[i], values[i], idxP1, idxP2, idxP1+lengthP)
				
				globidxQ += 1
				Amat[Qline,globidxQ] += -1
				idxQ = globidxQ
				
				idxP2 = idxP1 + lengthP + 1

	return 0

def build_Bvec(circuit,values,idxP1=0,idxP2=1,idxPout=-1) :
	'''
	circuit : list of components defined by their type in one letter
	values : same architecture as circuit, but with values corresponding to each element
	Amat : mass matrix
	Bvec : b vector of the system
	'''

	global Bvec
	global line
	global globidxQ
	idxQ = globidxQ

	if len(circuit)==0 :
		return

	if line == 0 :
		idxPout = nb_inc(circuit)[0]-1

	for i in range(len(circuit)):
		elem = circuit[i]

		if i == len(circuit)-1 and not isinstance(circuit[-1],list) :
			idxP2 = idxPout
			
		if elem == 'R' :                      # P1 - P2 = RQ
			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'C' :                    # Q = Cd(P1-P2) = CdP1 - CdP2
			Bvec[line] += -values[i]*P1[n]/Dt
			Bvec[line] += values[i]*P2[n]/Dt
			
			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'P' :                    # P1 - P2 = P
			Bvec[line] += values[i]
			
			idxP1 = idxP2
			idxP2 += 1
			line += 1
		
		elif isinstance(elem,list) :
			if isinstance(elem[0],list) :
				Qline = line
				line += 1

				lengthP = nb_inc([elem])[0] - 1

				idxP2_shift = 0
				for j in range(len(elem)) :
					globidxQ += 1
					build_Bvec(circuit[i][j], values[i][j], idxP1, idxP2+idxP2_shift, idxP1+lengthP)
					idxP2_shift += nb_inc(elem[j])[0] - 2
				
				idxP1 += lengthP
				idxP2 = idxP1+1
				
			else :
				Qline = line
				line += 1

				lengthP = nb_inc(elem)[0] - 1

				globidxQ += 1
				build_Bvec(circuit[i], values[i], idxP1, idxP2, idxP1+lengthP)
				
				globidxQ += 1
				idxQ = globidxQ
				
				idxP2 = idxP1 + lengthP + 1

	return 0

def init_cond(Q_in,P_out):
	global Amat
	global Bvec
	global nbP
	global line
	Amat[line,nbP] = 1
	Bvec[line] = Q_in
	line += 1
	Amat[line,nbP-1] = 1
	Bvec[line] = P_out
	
# build_Amat(circuitCoro,valuesCoro)
# build_Amat(circuitTem,valuesTem)
build_Amat(circuit,values)
build_Bvec(circuit,values)
# build_Amat(circuitCoroTem,valuesCoroTem)
init_cond(Qin,Pd)
print(Amat)
print(Bvec)
print(np.linalg.solve(Amat, Bvec))

nbP, nbQ = nb_inc(circuitCoro)
globidxQ = nbP
AmatDum = np.array([['│     ' for _ in range(nbP+nbQ)] for _ in range(nbP+nbQ)])
Bvec = np.zeros((nbP+nbQ))
line = 0

def build_AmatDum(circuit,values,idxP1=0,idxP2=1,idxPout=-1) :
	'''
	circuit : list of components defined by their type in one letter
	values : same architecture as circuit, but with values corresponding to each element
	Amat : mass matrix
	Bvec : b vector of the system
	'''

	global AmatDum
	global Bvec
	global line
	global globidxQ
	idxQ = globidxQ

	if len(circuit)==0 :
		return

	if line == 0 :
		idxPout = nb_inc(circuit)[0]-1

	for i in range(len(circuit)):
		elem = circuit[i]

		if i == len(circuit)-1 and not isinstance(circuit[-1],list) :
			idxP2 = idxPout
			
		if elem == 'R' :                      # P1 - P2 = RQ
			AmatDum[line,idxQ] = '│ -R  '
			AmatDum[line,idxP1] = '│ +1  '
			AmatDum[line,idxP2] = '│ -1  '

			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'C' :                    # Q = Cd(P1-P2) = CdP1 - CdP2
			AmatDum[line,idxQ] = '│ +1  '
			AmatDum[line,idxP1] = '│-C/Dt'
			# Bvec[line] += -values[i]*P1[n]/Dt
			AmatDum[line,idxP2] = '│+C/Dt'
			# Bvec[line] += values[i]*P2[n]/Dt
			
			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'P' :                    # P1 - P2 = P
			AmatDum[line,idxP1] = '│ +1  '
			AmatDum[line,idxP2] = '│ -1  '
			# Bvec[line] += values[i]
			
			idxP1 = idxP2
			idxP2 += 1
			line += 1

		elif elem == 'G' :                    # P1 - P2 = P
			AmatDum[line-1,idxP1] = '│  0  '
		
		elif isinstance(elem,list) :
			if isinstance(elem[0],list) :
				Qline = line
				AmatDum[Qline,idxQ] = '│ +1  '
				line += 1

				lengthP = nb_inc([elem])[0] - 1

				idxP2_shift = 0
				for j in range(len(elem)) :
					globidxQ += 1
					AmatDum[Qline,globidxQ] = '│ -1  '
					build_AmatDum(circuit[i][j], values[i][j], idxP1, idxP2+idxP2_shift, idxP1+lengthP)
					idxP2_shift += nb_inc(elem[j])[0] - 2
				
				idxP1 += lengthP
				idxP2 = idxP1+1
				
			else :
				Qline = line
				AmatDum[Qline,idxQ] = '│ +1  '
				line += 1

				lengthP = nb_inc(elem)[0] - 1

				globidxQ += 1
				AmatDum[Qline,globidxQ] = '│ -1  '
				build_AmatDum(circuit[i], values[i], idxP1, idxP2, idxP1+lengthP)
				
				globidxQ += 1
				AmatDum[Qline,globidxQ] = '│ -1  '
				idxQ = globidxQ
				
				idxP2 = idxP1+lengthP+1

	return 0

# build_AmatDum(circuitCoro,valuesCoro)
# for i in range(len(AmatDum)):
# 	linestr = ''
# 	for j in range(len(AmatDum[i])):
# 		linestr += AmatDum[i][j]
# 	print(linestr)
# globidxQ = nbP
# AmatDum = np.array([['│     ' for _ in range(nbP+nbQ)] for _ in range(nbP+nbQ)])
# Bvec = np.zeros((nbP+nbQ))
# line = 0
# build_AmatDum(circuitCoroTem,valuesCoroTem)
# print(' ')
# for i in range(len(AmatDum)):
# 	linestr = ''
# 	for j in range(len(AmatDum[i])):
# 		linestr += AmatDum[i][j]
# 	print(linestr)