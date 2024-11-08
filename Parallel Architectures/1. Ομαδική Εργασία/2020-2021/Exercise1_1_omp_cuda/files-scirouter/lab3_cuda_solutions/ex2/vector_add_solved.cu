#include <stdlib.h>
#include <stdio.h>
#include <string.h>

char *program_name = NULL;

double csecond(void) {
  struct timespec tms;

  if (clock_gettime(CLOCK_REALTIME, &tms)) {
    return (0.0);
  }
  /// seconds, multiplied with 1 million
  int64_t micros = tms.tv_sec * 1000000;
  /// Add full microseconds
  micros += tms.tv_nsec / 1000;
  /// round up if necessary
  if (tms.tv_nsec % 1000 >= 500) {
    ++micros;
  }
  return ((double)micros / 1000000.0);
}

static void check(cudaError_t result, char const *const func, const char *const file, int const line) {
  if (result) {
    printf("CUDA error at %s: %d code = %d (%s) %s\n", file, line, static_cast<unsigned int>(result), cudaGetErrorName(result), func);
    exit(EXIT_FAILURE);
  }
}
#define checkCudaErrors(val) check((val), #val, __FILE__, __LINE__)

static void set_program_name(char *path) {
  if (!program_name)
    program_name = strdup(path);
  if (!program_name)
    fprintf(stderr, "strdup failed\n");
}

static void print_usage() {
  printf("Usage: %s <N>\n", program_name);
}

__device__ 
int get_global_id(){
  return blockDim.x*blockIdx.x + threadIdx.x;
}

__global__ void vector_add(float *out, float *a, float *b, int n) {
  int tid = get_global_id();
  for (int i = tid; i < n; i+=blockDim.x*gridDim.x) {
    out[i] = a[i] + b[i];
  }
}

#define BLOCK_DIM 64
#define GRID_DIM 32

int main(int argc, char **argv) {
  set_program_name(argv[0]);
  if (argc < 2) {
    printf("Error in number of arguments!\n");
    print_usage();
    exit(1);
  }

  int N = atoi(argv[1]);
  float *a, *b, *out; 

  // Allocate memory for vectors ON CPU MEM
  a   = (float*)malloc(sizeof(float) * N);
  b   = (float*)malloc(sizeof(float) * N);
  out = (float*)malloc(sizeof(float) * N);

  //  Allocate memory for vectors ON GPU MEM
  float *dev_a, *dev_b, *dev_out; 
  checkCudaErrors(cudaMalloc((void**) &dev_a, sizeof(float) * N));
  checkCudaErrors(cudaMalloc((void**) &dev_b, sizeof(float) * N));
  checkCudaErrors(cudaMalloc((void**) &dev_out, sizeof(float) * N));

  //  Copy vectors to GPU MEM
  checkCudaErrors(cudaMemcpy(dev_a, a, sizeof(float) * N, cudaMemcpyHostToDevice));
  checkCudaErrors(cudaMemcpy(dev_b, b, sizeof(float) * N, cudaMemcpyHostToDevice));

  // Initialize vectors
  for (int i = 0; i < N; i++) {
    a[i] = 1.0f; b[i] = 2.0f;
  }

  double timer = csecond();

  dim3 block(BLOCK_DIM);
  dim3 grid(GRID_DIM);
  vector_add<<<grid, block>>>(dev_out, dev_a, dev_b, N);
  checkCudaErrors(cudaPeekAtLastError());
  checkCudaErrors(cudaDeviceSynchronize());

  timer = csecond() - timer;
  printf("Addition completed in %lf seconds!\n", timer);

  // Cleanup
  free(a);
  free(b);
  free(out);

  cudaFree(dev_a);
  cudaFree(dev_b);
  cudaFree(dev_out);

  return 0;
}
