#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main (int argc, char *argv[])
{
    int i;
    char *c;

    (void)printf ("argc is %d\n", argc);
    if (argc < 2)
    {
        (void)fprintf (stderr, "Please supply a string to convert.  Ta.");
        return EXIT_FAILURE;
    }

    printf ("I will now convert %s\n", argv[1]);
    c = argv[1];
    for (i=0 ; i<strlen(argv[1]) ; i++)
    {
        printf("%02X", *c);
        c++;
    }
    printf("\n");
    return EXIT_SUCCESS;
}