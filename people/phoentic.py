import regex as re
import numpy

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
    """
    Computes the Levenshtein distance between the two strings.  Returns a tuple containing
    the distance itself and also the entire matrix for further processing.
    See: https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm
    """
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

# Computes the Levenshtein distance between the two strings.  Returns a tuple containing the distance itself and also the entire matrix for further processing.
def wagner_fisher(s: str, t: str):
    m, n = len(s), len(t)
    d = numpy.zeros(shape=(m + 1, n + 1), dtype='int32')

    for i in range(1, m + 1):
        d[i, 0] = i

    for j in range(1, n + 1):
        d[0, j] = j

    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                substitutionCost = 0
            else:
                substitutionCost = 1

            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + substitutionCost)

    return d[m, n], d

# Compute the edit operations required to get from string s to string t
def edit_instructions(s: str, t: str):
    distance, d = wagner_fisher(s, t)
    m, n = len(s), len(t)
    instructions = []

    while m > 0 or n > 0:
        deletion_score = d[m - 1, n] if m >= 1 else float('inf')
        insertion_score = d[m, n - 1] if n >= 1 else float('inf')
        substitution_or_noop_score = d[m - 1, n - 1] if m >= 1 and n >= 1 else float('inf')
        smallest = min(deletion_score, insertion_score, substitution_or_noop_score)
        if smallest == substitution_or_noop_score:
            if d[m - 1, n - 1] < d[m, n]:
                instructions.append('substitute "%s" with "%s" at position %d' % (s[m - 1], t[n - 1], n - 1))
            m -= 1
            n -= 1
        elif smallest == deletion_score:
            instructions.append('delete "%s" at position %d' % (s[m - 1], n))
            m -= 1
        elif smallest == insertion_score:
            instructions.append('insert "%s" at position %d' % (t[n - 1], n - 1))
            n -= 1

    if distance != len(instructions):
        raise Exception('Internal error')

    return instructions[::-1]