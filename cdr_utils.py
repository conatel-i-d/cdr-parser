

def parse_standard(line, workbook, row):
    resultados = {
        0: 'Completada',
        1: 'Ocupado',
        2: 'Numero invalido',
        3: 'Lineas no disponibles',
        4: 'Abandono',
        5: 'No atendida',
        6: 'Problema de red',
        7: 'Desconocido',
        8: 'Cuenta no existente',
        9: 'No autorizado',
        10: 'LNP',
        11: 'LNP bis',
        12: 'Automatic Collect Call Blocking'
    }
    hoja = workbook.active
    hoja['A' + str(row)] = line[4]  # CDR field 5
    hoja['B' + str(row)] = line[5][-32:]  # CDR field 6
    hoja['C' + str(row)] = line[2]  # CDR field 3
    hoja['D' + str(row)] = line[3]  # CDR field 4
    hoja['E' + str(row)] = line[11]  # CDR field 12
    hoja['F' + str(row)] = line[10]  # CDR field 11
    try:
        hoja['G' + str(row)] = resultados[int(line[17])]  # CDR field 18
    except ValueError:
        # El campo esta vacio
        hoja['G' + str(row)] = 'NPI'  # CDR field 18
    hoja['H' + str(row)] = line[39]  # CDR field 40
    hoja['I' + str(row)] = line[40]  # CDR field 41
    hoja['J' + str(row)] = line[47]  # CDR field 48
    hoja['K' + str(row)] = line[48]  # CDR field 49
    hoja['M' + str(row)] = line[49]  # CDR field 50
    hoja['N' + str(row)] = line[50]  # CDR field 51
    hoja['L' + str(row)] = line[51]  # CDR field 52
    hoja['O' + str(row)] = line[52]  # CDR field 53



def parse_intermediate(line, workbook, row):
    pass


def parse_queue(line, workbook, row):
    resultados = {
        1: 'NO',
        2: 'SI'
    }
    hoja = workbook.active
    hoja['A' + str(row)] = line[4][-32:]  # CDR field 5
    hoja['B' + str(row)] = line[2]  # CDR field 3
    hoja['C' + str(row)] = line[6]  # CDR field 7
    hoja['D' + str(row)] = line[7]  # CDR field 8
    hoja['E' + str(row)] = line[8]  # CDR field 9
    hoja['F' + str(row)] = resultados[int(line[10])]  # CDR field 11
    hoja['G' + str(row)] = line[11]  # CDR field 12

def parse_call_forwarding(line, workbook, row):
    pass


def parse_long_call(line, workbook, row):
    pass


def parse_change_of_software(line, workbook, row):
    pass


def parse_feature(line, workbook, row):
    pass


def parse_half_call(line, workbook, row):
    pass


def parse_qos(line, workbook, row):
    pass

