#ifndef COMPRESSOR_H
#define COMPRESSOR_H

#include <string>
#include <vector>

int runCompressor(int size, int threads);

struct Token
{
    int offset;
    int length;
    char nextChar;
};

class Compressor
{
public:
    void generateFile(const std::string& filename,
                      size_t sizeMB);

    bool compressSequential(
        const std::string& inputFile,
        const std::string& outputFile);

    bool compressParallel(
        const std::string& inputFile,
        const std::string& outputFile,
        int threads);

    bool decompress(
        const std::string& inputFile,
        const std::string& outputFile);

    bool compareFiles(
        const std::string& file1,
        const std::string& file2);

private:
    static constexpr int WINDOW_SIZE = 255;
    static constexpr int LOOKAHEAD_SIZE = 32;
    static constexpr size_t BLOCK_SIZE = 1024 * 1024;

    std::vector<char> readFile(
        const std::string& filename);

    bool writeCompressed(
        const std::string& filename,
        const std::vector<Token>& tokens);

    std::vector<Token> compressBlock(
        const std::vector<char>& data,
        size_t start,
        size_t end);

    std::vector<char> decompressTokens(
        const std::vector<Token>& tokens);
};

#endif