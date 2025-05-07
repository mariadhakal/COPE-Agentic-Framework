#include <stdio.h>
#include <string.h>

int main() {
   char* str[5], temp[50];
   
   char str1[] = "R programming\n";
   char str2[] = "JavaScript\n";
   char str3[] = "Java\n";
   char str4[] = "C programming\n";
   char str5[] = "C++ programming\n";

   str[0] = str1;
   str[1] = str2;
   str[2] = str3;
   str[3] = str4;
   str[4] = str5;

   // storing strings in the lexicographical order
   for (int i = 0; i < 5; ++i) {
      for (int j = i + 1; j < 5; ++j) {

         // swapping strings if they are not in the lexicographical order
         if (strcmp(str[i], str[j]) > 0) {
            strcpy(temp, str[i]);
            strcpy(str[i], str[j]);
            strcpy(str[j], temp);
         }
      }
   }

   printf("\nIn the lexicographical order: \n");
   for (int i = 0; i < 5; ++i) {
      fputs(str[i], stdout);
   }
   return 0;
}