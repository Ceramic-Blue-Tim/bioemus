#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "getopt.h"
#include <time.h>

// % ./decode_raster_file --duration 10 --sep ';' --read-file "read.txt" --save-file "save.csv"

#define NB_NRN                  1024
#define NB_FRAME_PER_READ       100
#define DATAWIDTH_BIT           (sizeof(unsigned int)*8)
#define NB_SPK_DATA_PER_FRAME   (NB_NRN/DATAWIDTH_BIT)
#define FRAME_SIZE              (NB_SPK_DATA_PER_FRAME+1)

static unsigned long get_posix_clock_time_usec (){
    struct timespec ts;

    if (clock_gettime (CLOCK_MONOTONIC, &ts) == 0)
        return (unsigned long) (ts.tv_sec * 1000000 + ts.tv_nsec / 1000);
    else
        return 0;
}

int main(int argc, char const *argv[]){
    int duration_s   = 10;
    char* sep;
    char* fpath_read;
    char* fpath_save;

    // Define long options
    struct option long_options[] = {
        {"duration", required_argument, 0, 'd'},
        {"sep", required_argument, 0, 'p'},
        {"read-file", required_argument, 0, 'r'},
        {"save-file", required_argument, 0, 's'},
        {0, 0, 0, 0} // end of options marker
    };

    // Parse command line options
    int opt;
    while ((opt = getopt_long(argc, argv, "d:p:r:s", long_options, NULL)) != -1) {
        switch (opt) {
            case 'd':
                duration_s = atoi(optarg);
                break;
            case 'p':
                sep = optarg;
                break;
            case 'r':
                fpath_read = optarg;
                break;
            case 's':
                fpath_save = optarg;
                break;
            case '?':
                fprintf(stderr, "Unknown option: %c\n",optopt);
                return EXIT_FAILURE;
            default:
                fprintf(stderr, "Error parsing arguments\n");
                fprintf(stderr, "Usage:\n");
                fprintf(stderr, "[--duration duration to decode (s)]\n");
                fprintf(stderr, "[--sep file separator]\n");
                fprintf(stderr, "[--read-file path to read file]\n");
                fprintf(stderr, "[--save-file path to save file]\n");
                return EXIT_FAILURE;
        }
    }

    // Open read and save file
    FILE* fread_ptr;
    FILE* fsave_ptr;	
    fread_ptr = fopen(fpath_read, "r");
    fsave_ptr = fopen(fpath_save, "w");

    // Check opening
    if (fread_ptr == NULL){
        fprintf(stderr, "Error opening file to read\n");
        exit(EXIT_FAILURE);
    }
    if (fsave_ptr == NULL){
        fprintf(stderr, "Error opening saving file\n");
        exit(EXIT_FAILURE);
    }

    // Get size of file
    fseek(fread_ptr, 0, SEEK_END);              // seek to end of file
    long fread_byte_size = ftell(fread_ptr);    // get current file pointer
    long file_size       = fread_byte_size/sizeof(unsigned int);
    fseek(fread_ptr, 0, SEEK_SET);              // seek back to beginning of file

    unsigned int read_buffer[NB_FRAME_PER_READ*FRAME_SIZE];
    unsigned int x[NB_FRAME_PER_READ*NB_NRN]; // Maximum size is all neurons spiking at all frames
    unsigned int y[NB_FRAME_PER_READ*NB_NRN]; // Maximum size is all neurons spiking at all frames
    unsigned int write_cnt = 0;
    
    size_t read_size;
    unsigned int tstamp;

    // TODO : add handling for exception (lower/larger than buffer) + duration as argument
    // Read all file by NB_FRAME_PER_READ blocks
    unsigned int nb_read = (file_size>NB_FRAME_PER_READ*FRAME_SIZE)?(file_size/(NB_FRAME_PER_READ*FRAME_SIZE)):(1);
    fprintf(fsave_ptr, "time;neuron_id\n");
    for (int i = 0; i < nb_read ; i++){
        read_size  = fread(&read_buffer, NB_FRAME_PER_READ*FRAME_SIZE*sizeof(unsigned int), 1, fread_ptr);
        write_cnt = 0;        

        // unsigned long tstart = get_posix_clock_time_usec();

        // For each frame
        for (int j = 0; j < NB_FRAME_PER_READ; j++){
            tstamp = read_buffer[FRAME_SIZE*j];
            // printf("tstamp: %u\n", tstamp);
            // For all spike registers
            for (int k = 0; k < NB_SPK_DATA_PER_FRAME; k++){
                // printf("reg%d: %u\n", k, read_buffer[FRAME_SIZE*j + k + 1]);
                // Detect spike for all bits
                for (int b = 0; b < DATAWIDTH_BIT; b++){
                    if ((read_buffer[FRAME_SIZE*j + k + 1] & (1<<b)) != 0){
                        x[write_cnt] = tstamp;
                        y[write_cnt] = DATAWIDTH_BIT*k + b;
                        write_cnt++;
                    }
                }
            }
        }
        // unsigned long tstop = get_posix_clock_time_usec();
        // printf("Elasped time: %lu µs\n", tstop-tstart);
        
        // Write in file
        for (int z = 0; z < write_cnt; z++){
            fprintf(fsave_ptr, "%u;%u\n", x[z], y[z]);
        }        
    }

    fclose(fread_ptr);
    fclose(fsave_ptr);

    return EXIT_SUCCESS;
}
