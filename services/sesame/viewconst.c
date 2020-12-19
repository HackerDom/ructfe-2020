 #include <sys/types.h>
 #include <sys/stat.h>
 #include <fcntl.h>


int main()
{
	printf("%d %d\n", O_RDWR, O_CREAT);
	return 0;
}
