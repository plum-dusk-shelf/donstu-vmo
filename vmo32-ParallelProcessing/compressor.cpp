#include "compressor.h"

#include <fstream>
#include <iostream>
#include <random>
#include <omp.h>
#include <chrono>
#include <filesystem>
#include <cstring>
using namespace std;

int runCompressor(int size, int threads) {
    Compressor compressor;

    std::filesystem::path workDir = "C:/Users/simafrus/CPP/PCDA/";
    std::string inputFile = (workDir / "input.txt").string();
    std::string seqFile = (workDir / "seq.bin").string();
    std::string parFile = (workDir / "par.bin").string();
    std::string restoreFile = (workDir / "restore.txt").string();
    std::string resultsFile = (workDir / "results.csv").string();

    auto start0 =
        std::chrono::high_resolution_clock::now();

    compressor.generateFile(
        inputFile,
        size
    );

    auto end0 =
        std::chrono::high_resolution_clock::now();

    auto genTime =
        std::chrono::duration_cast<
            std::chrono::milliseconds>(
            end0 - start0);

    cout << "File of size " << size << " generation: " << genTime.count() << "ms" << endl;

    auto start1 =
        std::chrono::high_resolution_clock::now();

    compressor.compressSequential(
        inputFile,
        seqFile
    );

    auto end1 =
        std::chrono::high_resolution_clock::now();

    auto seqTime =
        std::chrono::duration_cast<
            std::chrono::milliseconds>(
            end1 - start1);

    std::cout
        << "Sequential: "
        << seqTime.count()
        << " ms\n";

    auto start2 =
        std::chrono::high_resolution_clock::now();

    compressor.compressParallel(
        inputFile,
        parFile,
        threads
    );

    auto end2 =
        std::chrono::high_resolution_clock::now();

    auto parTime =
        std::chrono::duration_cast<
            std::chrono::milliseconds>(
            end2 - start2);

    std::cout
        << "Parallel "
        << "(" << threads << " threads): "
        << parTime.count()
        << " ms\n";

    double speedup =
        static_cast<double>(
            seqTime.count()) /
            parTime.count();

    std::cout
        << "Speedup: "
        << speedup << " times"
        << std::endl;

    compressor.decompress(
        parFile,
        restoreFile
    );

    bool equal =
    compressor.compareFiles(
        inputFile,
        restoreFile
    );

    if (equal)
    {
        std::cout
            << "Files are identical\n";
    }
    else
    {
        std::cout
            << "Files differ\n";
    }

    ofstream out(resultsFile, std::ios::app);
    // out << "size,seqTime,parTime,threads,speedup%" << endl;
    out << size << ";"
        << seqTime.count() << ";"
        << parTime.count() << ";"
        << threads << ";"
        << speedup<< ";"
        << speedup / threads << "\n";

    return 0;
}


std::vector<char>
Compressor::readFile(const std::string& filename)
{
    std::ifstream file(filename, std::ios::binary);

    if (!file)
        return {};

    file.seekg(0, std::ios::end);

    size_t size = file.tellg();

    file.seekg(0, std::ios::beg);

    std::vector<char> data(size);

    file.read(data.data(), size);

    return data;
}

void Compressor::generateFile(
    const std::string& filename,
    size_t size)
{
    std::ofstream file(filename, std::ios::binary);

    std::mt19937 rng(std::random_device{}());

    std::uniform_int_distribution<int> dist(0, 3);

    const char patterns[] =
    {
        'A', 'B', 'C', 'D'
    };

    size_t totalBytes =
        size;

    for (size_t i = 0; i < totalBytes; ++i)
    {
        char c = patterns[dist(rng)];

        file.write(&c, 1);
    }

    file.close();
}

std::vector<Token>
Compressor::compressBlock(
    const std::vector<char>& data,
    size_t start,
    size_t end)
{
    std::vector<Token> tokens;

    size_t i = start;

    while (i < end)
    {
        int bestLength = 0;
        int bestOffset = 0;

        size_t searchStart =
            (i > WINDOW_SIZE)
            ? i - WINDOW_SIZE
            : start;

        for (size_t j = searchStart;
             j < i;
             ++j)
        {
            int length = 0;

            while (
                length < LOOKAHEAD_SIZE &&
                i + length < end &&
                data[j + length] ==
                data[i + length]
            )
            {
                length++;
            }

            if (length > bestLength)
            {
                bestLength = length;
                bestOffset =
                    static_cast<int>(i - j);
            }
        }

        Token token;

        token.offset = bestOffset;
        token.length = bestLength;

        if (i + bestLength < end)
            token.nextChar =
                data[i + bestLength];
        else
            token.nextChar = 0;

        tokens.push_back(token);

        i += bestLength + 1;
    }

    return tokens;
}

bool Compressor::writeCompressed(
    const std::string& filename,
    const std::vector<Token>& tokens)
{
    std::ofstream file(filename,
                       std::ios::binary);

    if (!file)
        return false;

    size_t count = tokens.size();

    file.write(
        reinterpret_cast<char*>(&count),
        sizeof(count));

    file.write(
        reinterpret_cast<const char*>(
            tokens.data()),
        count * sizeof(Token));

    return true;
}

bool Compressor::compressSequential(
    const std::string& inputFile,
    const std::string& outputFile)
{
    auto data = readFile(inputFile);

    if (data.empty())
        return false;

    auto tokens =
        compressBlock(data, 0, data.size());

    return writeCompressed(
        outputFile,
        tokens);
}

bool Compressor::compressParallel(
    const std::string& inputFile,
    const std::string& outputFile,
    int threads)
{
    auto data = readFile(inputFile);

    if (data.empty())
        return false;

    size_t numBlocks =
        (data.size() + BLOCK_SIZE - 1)
        / BLOCK_SIZE;

    std::vector<std::vector<Token>>
        blockTokens(numBlocks);

    omp_set_num_threads(threads);

#pragma omp parallel for
    for (int i = 0;
         i < static_cast<int>(numBlocks);
         ++i)
    {
        size_t start = i * BLOCK_SIZE;

        size_t end =
            std::min(
                start + BLOCK_SIZE,
                data.size());

        blockTokens[i] =
            compressBlock(data,
                          start,
                          end);
    }

    std::vector<Token> allTokens;

    for (auto& block : blockTokens)
    {
        allTokens.insert(
            allTokens.end(),
            block.begin(),
            block.end());
    }

    return writeCompressed(
        outputFile,
        allTokens);
}

std::vector<char>
Compressor::decompressTokens(
    const std::vector<Token>& tokens)
{
    std::vector<char> output;

    for (const auto& token : tokens)
    {
        if (token.offset == 0 &&
            token.length == 0)
        {
            output.push_back(
                token.nextChar);

            continue;
        }

        size_t start =
            output.size() -
            token.offset;

        for (int i = 0;
             i < token.length;
             ++i)
        {
            output.push_back(
                output[start + i]);
        }

        if (token.nextChar != 0)
        {
            output.push_back(
                token.nextChar);
        }
    }

    return output;
}

bool Compressor::decompress(
    const std::string& inputFile,
    const std::string& outputFile)
{
    std::ifstream file(inputFile,
                       std::ios::binary);

    if (!file)
        return false;

    size_t count;

    file.read(
        reinterpret_cast<char*>(&count),
        sizeof(count));

    std::vector<Token> tokens(count);

    file.read(
        reinterpret_cast<char*>(
            tokens.data()),
        count * sizeof(Token));

    auto data =
        decompressTokens(tokens);

    std::ofstream out(outputFile,
                      std::ios::binary);

    out.write(data.data(),
              data.size());

    return true;
}

bool Compressor::compareFiles(
    const std::string& file1,
    const std::string& file2)
{
    std::ifstream f1(file1,
                     std::ios::binary);

    std::ifstream f2(file2,
                     std::ios::binary);

    if (!f1 || !f2)
        return false;

    f1.seekg(0, std::ios::end);
    f2.seekg(0, std::ios::end);

    size_t size1 = f1.tellg();
    size_t size2 = f2.tellg();

    if (size1 != size2)
    {
        std::cout
            << "Different file sizes\n";

        return false;
    }

    f1.seekg(0, std::ios::beg);
    f2.seekg(0, std::ios::beg);

    const size_t BUFFER_SIZE = 4096;

    char buffer1[BUFFER_SIZE];
    char buffer2[BUFFER_SIZE];

    while (f1 && f2)
    {
        f1.read(buffer1, BUFFER_SIZE);
        f2.read(buffer2, BUFFER_SIZE);

        std::streamsize bytes1 =
            f1.gcount();

        std::streamsize bytes2 =
            f2.gcount();

        if (bytes1 != bytes2)
            return false;

        if (memcmp(buffer1,
                   buffer2,
                   bytes1) != 0)
        {
            return false;
        }
    }

    return true;
}