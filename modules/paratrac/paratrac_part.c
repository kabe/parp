#include <stdio.h>
#include <paratrac_part.h>

unsigned int util_str_hash(const char *str)
{
    unsigned int hash = 0;
    int i = 0;

    while (str[i]) {
        hash += str[i] * (i + 1);
        i++;
    }
    return hash;

}
