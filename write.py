def calc_checksum(file):
    sum = 0
    with open(file, 'r') as f:
        data = f.read()
        for i in range(len(data)):
            sum = sum + ord(data[i])

    temp = sum % 256
    rem = -temp
    return '%2X' % (rem & 0xFF)


print(calc_checksum("test"))
