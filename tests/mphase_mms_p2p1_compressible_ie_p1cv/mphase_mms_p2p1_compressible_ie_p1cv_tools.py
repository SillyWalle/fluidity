from math import sin, cos, tanh, pi, sqrt

def u1(X):
    return sin(X[0]**2 + X[1]**2) + 0.500

def v1(X):
    return 0.100*cos(X[0]**2 + X[1]**2) + 0.0500

def p(X):
    return (0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))

def rho1(X):
    return 0.500*sin(X[0]**2 + X[1]**2) + 0.750

def ie1(X):
    return 1.25*X[0]*X[1] + cos(X[0] + X[1])

def vfrac1(X):
    return 0.800

def forcing_u1(X):
    return 2*(0.100*cos(X[0]**2 + X[1]**2) + 0.0500)*(0.400*sin(X[0]**2 + X[1]**2) + 0.600)*X[1]*cos(X[0]**2 + X[1]**2) + 2*(0.400*sin(X[0]**2 + X[1]**2) + 0.600)*(sin(X[0]**2 + X[1]**2) + 0.500)*X[0]*cos(X[0]**2 + X[1]**2) + 0.800*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[0]*cos(X[0]**2 + X[1]**2) + 2.24*X[0]**2*sin(X[0]**2 + X[1]**2) + 2.24*X[1]**2*sin(X[0]**2 + X[1]**2) + 0.800*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[1] - 0.400*sin(X[0] + X[1])) - 0.282842712400000*sin(X[0]**2 + X[1]**2) - 2.24*cos(X[0]**2 + X[1]**2) - 0.424264068600000

def forcing_v1(X):
    return -0.200*(0.100*cos(X[0]**2 + X[1]**2) + 0.0500)*(0.400*sin(X[0]**2 + X[1]**2) + 0.600)*X[1]*sin(X[0]**2 + X[1]**2) - 0.200*(0.400*sin(X[0]**2 + X[1]**2) + 0.600)*(sin(X[0]**2 + X[1]**2) + 0.500)*X[0]*sin(X[0]**2 + X[1]**2) + 0.800*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[1]*cos(X[0]**2 + X[1]**2) + 0.224*X[0]**2*cos(X[0]**2 + X[1]**2) + 0.224*X[1]**2*cos(X[0]**2 + X[1]**2) + 0.800*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[0] - 0.400*sin(X[0] + X[1])) - 0.0588427124000001*sin(X[0]**2 + X[1]**2) - 0.424264068600000

def forcing_rho1(X):
    return (0.0800*cos(X[0]**2 + X[1]**2) + 0.0400)*X[1]*cos(X[0]**2 + X[1]**2) + 1.60*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*X[0]*cos(X[0]**2 + X[1]**2) - 0.160*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*X[1]*sin(X[0]**2 + X[1]**2) + (0.800*sin(X[0]**2 + X[1]**2) + 0.400)*X[0]*cos(X[0]**2 + X[1]**2) + (0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(-0.400*X[0]*sin(X[0]**2 + X[1]**2) + 0.500) + 0.100*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*X[0]

def forcing_ie1(X):
    return 1.60*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[0]*cos(X[0]**2 + X[1]**2) - 0.160*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[1]*sin(X[0]**2 + X[1]**2) + (0.100*cos(X[0]**2 + X[1]**2) + 0.0500)*(0.400*sin(X[0]**2 + X[1]**2) + 0.600)*(1.25*X[0] - sin(X[0] + X[1])) + (0.400*sin(X[0]**2 + X[1]**2) + 0.600)*(sin(X[0]**2 + X[1]**2) + 0.500)*(1.25*X[1] - sin(X[0] + X[1])) - (152.330661657328*((0.0500*sin(X[0]**2 + X[1]**2) + 0.0750)*sqrt((-0.500*X[0]*X[1] + 0.100*cos(X[0]**2 + X[1]**2) + 0.0500)**2 + (-2.50*X[0] + sin(X[0]**2 + X[1]**2) - cos(X[0]**2 + X[1]**2) + 0.500)**2))**0.700 + 1102.64843906307*((0.0500*sin(X[0]**2 + X[1]**2) + 0.0750)*sqrt((-0.500*X[0]*X[1] + 0.100*cos(X[0]**2 + X[1]**2) + 0.0500)**2 + (-2.50*X[0] + sin(X[0]**2 + X[1]**2) - cos(X[0]**2 + X[1]**2) + 0.500)**2))**0.200 + 132.)*(-0.00178571428571429*X[0]*X[1] + 0.00142857142857143*sin(X[0]*X[1]) - 0.00142857142857143*cos(X[0] + X[1]))

def velocity1(X):
   return [u1(X), v1(X)]

def forcing_velocity1(X):
   return [forcing_u1(X), forcing_v1(X)]

def u2(X):
    return 2.50*X[0] + cos(X[0]**2 + X[1]**2)

def v2(X):
    return 0.500*X[0]*X[1]

def rho2(X):
    return 2.00

def ie2(X):
    return sin(X[0]*X[1])

def vfrac2(X):
    return 0.200

def forcing_u2(X):
    return -0.400*X[0]*X[1]**2*sin(X[0]**2 + X[1]**2) + 0.200*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[0]*cos(X[0]**2 + X[1]**2) + 0.560*X[0]**2*cos(X[0]**2 + X[1]**2) + 0.560*X[1]**2*cos(X[0]**2 + X[1]**2) + 0.200*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[1] - 0.400*sin(X[0] + X[1])) - (2.00*X[0]*sin(X[0]**2 + X[1]**2) - 2.50)*(1.00*X[0] + 0.400*cos(X[0]**2 + X[1]**2)) + 0.560*sin(X[0]**2 + X[1]**2) - 0.282842712400000

def forcing_v2(X):
    return 0.200*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[1]*cos(X[0]**2 + X[1]**2) + 0.100*X[0]**2*X[1] + 0.200*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[0] - 0.400*sin(X[0] + X[1])) + 0.500*(1.00*X[0] + 0.400*cos(X[0]**2 + X[1]**2))*X[1] - 0.282842712400000

def forcing_ie2(X):
    return 0.200*X[0]**2*X[1]*cos(X[0]*X[1]) - 0.200*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(2.00*X[0]*sin(X[0]**2 + X[1]**2) - 2.50)*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1])) + 0.100*(0.500*sin(X[0]**2 + X[1]**2) + 0.750)*(0.500*X[0]*X[1] + 0.400*cos(X[0] + X[1]))*X[0] + (1.00*X[0] + 0.400*cos(X[0]**2 + X[1]**2))*X[1]*cos(X[0]*X[1]) + (152.330661657328*((0.0500*sin(X[0]**2 + X[1]**2) + 0.0750)*sqrt((-0.500*X[0]*X[1] + 0.100*cos(X[0]**2 + X[1]**2) + 0.0500)**2 + (-2.50*X[0] + sin(X[0]**2 + X[1]**2) - cos(X[0]**2 + X[1]**2) + 0.500)**2))**0.700 + 1102.64843906307*((0.0500*sin(X[0]**2 + X[1]**2) + 0.0750)*sqrt((-0.500*X[0]*X[1] + 0.100*cos(X[0]**2 + X[1]**2) + 0.0500)**2 + (-2.50*X[0] + sin(X[0]**2 + X[1]**2) - cos(X[0]**2 + X[1]**2) + 0.500)**2))**0.200 + 132.)*(-0.00178571428571429*X[0]*X[1] + 0.00142857142857143*sin(X[0]*X[1]) - 0.00142857142857143*cos(X[0] + X[1]))

def velocity2(X):
   return [u2(X), v2(X)]

def forcing_velocity2(X):
   return [forcing_u2(X), forcing_v2(X)]

