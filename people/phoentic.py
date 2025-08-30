import regex as re

# Character to Code map, this way for visibility
soundexMap = {
    "A": '0',
    "B": '1',
    "C": '2',
    "D": '3',
    "E": '0',
    "F": '1',
    "G": '2',
    "H": '9',
    "I": '0',
    "J": '2',
    "K": '2',
    "L": '4',
    "M": '5',
    "N": '5',
    "O": '0',
    "P": '1',
    "Q": '2',
    "R": '6',
    "S": '2',
    "T": '3',
    "U": '0',
    "V": '1',
    "W": '9',
    "Y": '9',
    "X": '2',
    "Z": '2',
}

# A phonetic algorithm for indexing names by sound, as pronounced in English. Will have trouble with Irish Names that are not Anglicised.
def soundex(input : str) -> str :
    # Defensive Checks

    # Null check
    if input is None :
        #print(input + ' is none')
        return None

    # TODO NumPy / Pandas Nan Check?

    # convert to uppercase for ease of use
    inputUpper = input.upper()

    # ensure that there is at least 1 character, and that all characters are letters
    nameRegex = r'^\p{L}+$'
    if not re.search(nameRegex,inputUpper):
        #print(inputUpper + ' is not word')
        return None

    # Algorithm Start

    # output, length will always end up as 4
    output = ''
    coded = ''

    # Retain first letter
    output += inputUpper[0]
    # Get Code for Stack Calculations
    coded += soundexMap.get(inputUpper[0],'8') # TODO Better Defensive Encoding check for Non-English Characters

    vowelRegex = r'[AEIOUYHW]'
    for index, letter in enumerate(inputUpper[1:], 1):
        if re.search(vowelRegex,letter): # skip vowels, 'Y', 'H' and 'W' after the first
            coded += soundexMap.get(letter,'8')
        else:
            code = soundexMap.get(letter,'8')
            last = coded[-1]

            if last == '9' and  len(coded) > 1: # Handle 'Y', 'H' and 'W' special case -> letters with the same code either side count as one
                last = coded[-2]

            coded += code
        #    print('last is ' + last + ', code is ' + code)
            if last != code and code != '8': # retain code if it differs from previous one
                output += code
      #          print('output is now ' + output)

    while len(output) < 4:
        output += '0' # Fill spaces with 0

    return output[:4]  # only return first 4 characters