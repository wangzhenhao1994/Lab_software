import numpy as np

class Calibration_mass():
    def __init__(self, mass=[18.0153,30], pixel=[1028,]):
        self.mass = mass
        self.pixels = pixel
        #the mass and correspongding pixel number


    def cal_k_b(self):
        a = np.array([[np.sqrt(self.mass[0]), 1], [np.sqrt(self.mass[1]), 1]])
        b = np.array([self.pixels[0], self.pixels[1]])
        [k, b] = np.linalg.solve(a, b)
        #print('k is ' + str(round(k, 1)), '\n', 'b is ' + str(round(b, 1)))
        return [k, b]

    def cal_pixel(self, _mass):
        def pix(x): return np.round(x[0]*np.sqrt(_mass)+x[1])
        #print('The pixel number of mass' + str(_mass) + ' is ' +
        #    str(np.round(pix(self.cal_k_b()))))
        return pix(self.cal_k_b())
    
    def pixel2mass(self, t):
        [k,b]=self.cal_k_b()
        return ((t-b)/k)**2
        
if __name__ == '__main__':
    cal = Calibration_mass()
    cal.cal_k_b()
    #print(cal.pixel2mass(641))
    print(cal.cal_pixel(30.0260))
