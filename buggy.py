import time
print('Starting buggy')
for i in range(5):
    print(f'Startng epoch {i}/5.')
    time.sleep(2)
    
print('Now bugging out.')
division_zero = 1 / 0