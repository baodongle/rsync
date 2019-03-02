#!/usr/bin/env python

import difflib


s1 = list('oooooSRoM')
s2 = list('oooooSooo')

print('Initial data:')
print('s1 =', s1)
print('s2 =', s2)
print('s1 == s2:', s1 == s2)
print()

matcher = difflib.SequenceMatcher(None, s1, s2)
for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):

    if tag == 'delete':
        print('Remove {} from positions [{}:{}]'.format(
            ''.join(s1[i1:i2]), i1, i2))
        print('  before =', ''.join(s1))
        del s1[i1:i2]

    elif tag == 'equal':
        print('s1[{}:{}] and s2[{}:{}] are the same'.format(
            i1, i2, j1, j2))

    elif tag == 'insert':
        print('Insert {} from s2[{}:{}] into s1 at {}'.format(
            ''.join(s2[j1:j2]), j1, j2, i1))
        print('  before =', ''.join(s1))
        s1[i1:i2] = s2[j1:j2]

    elif tag == 'replace':
        print(('Replace {} from s1[{}:{}] '
               'with {} from s2[{}:{}]').format(
                   ''.join(s1[i1:i2]), i1, i2, ''.join(s2[j1:j2]), j1, j2))
        print('  before =', ''.join(s1))
        s1[i1:i2] = s2[j1:j2]

    print('   after =', ''.join(s1), '\n')
