pair_combinations = ['AT', 'TA', 'GC', 'CG']


def is_base_pair(base1, base2):
    """(str, str) -> bool

    Returns True if the two chemical bases form a base pair

    >>>is_base_pair('A', 'T')
    True
    >>>is_base_pair('G', 'A')
    False
    """
    return base1 + base2 in pair_combinations


def is_dna(strand1, strand2):
    for i in range(len(strand1)):
        if strand1[i] + strand2[i] not in pair_combinations:
            return False
    return True


def is_dna_palindrome(strand1, strand2):
    reversed_strand = ''
    i = len(strand1)
    while i != 0:
        i -= 1
        reversed_strand += strand1[i]
    return reversed_strand == strand2


def restriction_sites(strand, sequence):
    """(str, str) -> list of int

    Returns the indices at which the sequence can be found in the strand

    >>>restriction_sites('ATGCAT', 'A')
    [0, 4]
    >>>restriction_sites('ATGCTAGCTAGCTA', 'TG')
    [1]
    >>>restriction_sites('ATTATAGA', 'CT')
    []
    """
    sites = []
    while sequence in strand:
        sites.append(strand.find(sequence))
        strand = strand.replace(sequence, 'X' * len(sequence), 1)

    return sites


def match_enzymes(strand, enzyme, sequence):
    """ (str, list of str, list of str) - > list of (str, int) tuples

    Returns a list of tuples containing the enzyme names alongside the index they are found at.

    >>>match_enzymes('CGCGATAGGATCC', ['BamHI'], ['GGATCC'])
    [(BamHI, [7])]
    >>>match_enzymes('AGCTAGCTGCGTATCGA', ['TaqI', 'AluI'], ['TCGA', 'AGCT'])
    [('TaqI', [13]), ('AluI', [0, 4])]
    """
    enzyme_locations = []

    for i in range(len(enzyme)):
        locations = []
        original = strand
        while sequence[i] in original:
            locations.append(original.find(sequence[i]))
            original = original.replace(sequence[i], 'X' * len(sequence[i]), 1)
        enzyme_locations.append((enzyme[i], locations))
    return enzyme_locations


def one_cutters(strand, enzyme, sequence):
    """(str, list of str, list of str) -> list of (str, int) tuples

    Returns a list of tuples containing the names and indices of enzymes that appear only once
    >>>one_cutters('ATGTGATCCAC', ['JohnHI', 'MonHI'], ['AC', 'AT'])
    [('JonHI', 9)]
    """
    all_enzymes = match_enzymes(strand, enzyme, sequence)
    one_cutters = []
    for i in range(len(all_enzymes)):
        if len(all_enzymes[i][1]) < 2:
            one_cutters.append(all_enzymes[i])
    return one_cutters


def correct_mutations(mutated, clean, enzyme, sequence):
    """(list of str, str, list of str, list of str_ -> NoneType

    Finds a common one-cutter between the clean and mutated strands, then edits the mutated strand from the one-cutter
    to be the sequence of the clean strand past the one-cutter

    >>>
    """
    clean_cutters = one_cutters(clean, enzyme, sequence)

    for bad_dna in mutated:
        mutated_cutter = one_cutters(bad_dna, enzyme, sequence)
        for cutter in clean_cutters:
            if mutated_cutter != [] and mutated_cutter[0][1] != []:
                if cutter[0] == mutated_cutter[0][0]:
                    mutated[mutated.index(bad_dna)] = bad_dna[:mutated_cutter[0][1][0]] + clean[cutter[1][0]:]
