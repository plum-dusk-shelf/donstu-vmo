// lz4_parallel.cpp
#include "lz4_parallel.h"

#include <fstream>
#include <iostream>
#include <cstring>
#include <omp.h>
#include <chrono>

#include <lz4.h>
#include "lab5.h"
#include <filesystem>

void run_lz4() {
    LZ4ParallelCompressor compressor;

    std::filesystem::path workDir = "C:/Users/simafrus/CPP/PCDA/";
    std::string inputFile = (workDir / "input.txt").string();
    std::string restoreFile = (workDir / "restore.txt").string();
    std::string outputFile = (workDir / "compressed.lz4p").string();

    auto start =
        std::chrono::high_resolution_clock::now();


    bool ok = compressor.compressFile(
        inputFile,
        outputFile
    );

    auto end =
        std::chrono::high_resolution_clock::now();

    if (!ok)
    {
        std::cout << "Compression failed\n";
        return;
    }

    auto duration =
        std::chrono::duration_cast<
            std::chrono::milliseconds
        >(end - start);

    std::cout << "Compression time: "
              << duration.count()
              << " ms\n";

    ok = compressor.decompressFile(
        outputFile,
       restoreFile
    );

    if (!ok)
    {
        std::cout << "Decompression failed\n";
        return;
    }

    std::cout << "Done\n";
}

LZ4ParallelCompressor::LZ4ParallelCompressor(size_t blockSize)
    : blockSize(blockSize)
{
}

std::vector<char> LZ4ParallelCompressor::readFile(const std::string& path)
{
    std::ifstream file(path, std::ios::binary);

    if (!file)
        return {};

    file.seekg(0, std::ios::end);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<char> data(size);
    file.read(data.data(), size);

    return data;
}

bool LZ4ParallelCompressor::writeFile(const std::string& path,
                                      const std::vector<char>& data)
{
    std::ofstream file(path, std::ios::binary);

    if (!file)
        return false;

    file.write(data.data(), data.size());

    return true;
}

std::vector<char> LZ4ParallelCompressor::compressBlock(const char* data,
                                                       size_t size)
{
    int maxDstSize = LZ4_compressBound(static_cast<int>(size));

    std::vector<char> compressed(maxDstSize);

    int compressedSize = LZ4_compress_default(
        data,
        compressed.data(),
        static_cast<int>(size),
        maxDstSize
    );

    if (compressedSize <= 0)
        return {};

    compressed.resize(compressedSize);

    return compressed;
}

std::vector<char> LZ4ParallelCompressor::decompressBlock(
    const char* data,
    size_t compressedSize,
    size_t originalSize)
{
    std::vector<char> decompressed(originalSize);

    int result = LZ4_decompress_safe(
        data,
        decompressed.data(),
        static_cast<int>(compressedSize),
        static_cast<int>(originalSize)
    );

    if (result < 0)
        return {};

    return decompressed;
}

bool LZ4ParallelCompressor::compressFile(
    const std::string& inputPath,
    const std::string& outputPath)
{
    auto input = readFile(inputPath);

    std::cout << "Input size: "
          << input.size()
          << std::endl;

    if (input.empty())
        return false;

    size_t totalSize = input.size();

    size_t numBlocks =
        (totalSize + blockSize - 1) / blockSize;

    std::vector<std::vector<char>> compressedBlocks(numBlocks);
    std::vector<uint32_t> originalSizes(numBlocks);
    std::vector<uint32_t> compressedSizes(numBlocks);

#pragma omp parallel for
    for (int i = 0; i < static_cast<int>(numBlocks); ++i)
    {
        size_t offset = i * blockSize;

        size_t currentBlockSize =
            std::min(blockSize, totalSize - offset);

        originalSizes[i] =
            static_cast<uint32_t>(currentBlockSize);

        compressedBlocks[i] =
            compressBlock(input.data() + offset,
                          currentBlockSize);

        compressedSizes[i] =
            static_cast<uint32_t>(
                compressedBlocks[i].size()
            );
    }

    std::ofstream out(outputPath, std::ios::binary);

    if (!out)
        return false;

    out.write(reinterpret_cast<char*>(&numBlocks),
              sizeof(numBlocks));

    for (size_t i = 0; i < numBlocks; ++i)
    {
        out.write(reinterpret_cast<char*>(&originalSizes[i]),
                  sizeof(uint32_t));

        out.write(reinterpret_cast<char*>(&compressedSizes[i]),
                  sizeof(uint32_t));

        out.write(compressedBlocks[i].data(),
                  compressedBlocks[i].size());
    }

    out.close();

    return true;
}

bool LZ4ParallelCompressor::decompressFile(
    const std::string& inputPath,
    const std::string& outputPath)
{
    std::ifstream in(inputPath, std::ios::binary);

    if (!in)
        return false;

    size_t numBlocks;

    in.read(reinterpret_cast<char*>(&numBlocks),
            sizeof(numBlocks));

    std::vector<std::vector<char>> compressedBlocks(numBlocks);
    std::vector<uint32_t> originalSizes(numBlocks);
    std::vector<uint32_t> compressedSizes(numBlocks);

    for (size_t i = 0; i < numBlocks; ++i)
    {
        in.read(reinterpret_cast<char*>(&originalSizes[i]),
                sizeof(uint32_t));

        in.read(reinterpret_cast<char*>(&compressedSizes[i]),
                sizeof(uint32_t));

        compressedBlocks[i].resize(compressedSizes[i]);

        in.read(compressedBlocks[i].data(),
                compressedSizes[i]);
    }

    in.close();

    std::vector<std::vector<char>> decompressedBlocks(numBlocks);

#pragma omp parallel for
    for (int i = 0; i < static_cast<int>(numBlocks); ++i)
    {
        decompressedBlocks[i] =
            decompressBlock(
                compressedBlocks[i].data(),
                compressedSizes[i],
                originalSizes[i]
            );
    }

    std::ofstream out(outputPath, std::ios::binary);

    if (!out)
        return false;

    for (size_t i = 0; i < numBlocks; ++i)
    {
        out.write(decompressedBlocks[i].data(),
                  decompressedBlocks[i].size());
    }

    out.close();

    return true;
}