// lz4_parallel.h
#ifndef LZ4_PARALLEL_H
#define LZ4_PARALLEL_H

#include <string>
#include <vector>
#include <cstdint>

void run_lz4();

class LZ4ParallelCompressor {
public:
    explicit LZ4ParallelCompressor(size_t blockSize = 1024 * 1024);

    bool compressFile(const std::string& inputPath,
                      const std::string& outputPath);

    bool decompressFile(const std::string& inputPath,
                        const std::string& outputPath);

private:
    size_t blockSize;

    std::vector<char> readFile(const std::string& path);
    bool writeFile(const std::string& path,
                   const std::vector<char>& data);

    std::vector<char> compressBlock(const char* data, size_t size);
    std::vector<char> decompressBlock(const char* data,
                                      size_t compressedSize,
                                      size_t originalSize);
};

#endif