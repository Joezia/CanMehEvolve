
void Decode::UpdateEndianness(FIT_UINT8 type, FIT_UINT8 size)
{
    FIT_UINT8 typeSize = baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK];
    if (typeSize <= 1 || (type & FIT_BASE_TYPE_ENDIAN_FLAG) == 0 ||
        (archs[localMesgIndex] & FIT_ARCH_ENDIAN_MASK) == FIT_ARCH_ENDIAN_LITTLE) {
        return;
    }

    FIT_UINT8 numElements = size / typeSize;
    // Process in-place byte-swapping using optimized loops for common sizes
    switch (typeSize) {
        case 2:
            for (FIT_UINT8 i = 0; i < numElements; ++i) {
                std::swap(fieldData[i * 2], fieldData[i * 2 + 1]);
            }
            break;
        case 4:
            for (FIT_UINT8 i = 0; i < numElements; ++i) {
                FIT_UINT8* p = &fieldData[i * 4];
                std::swap(p[0], p[3]);
                std::swap(p[1], p[2]);
            }
            break;
        case 8:
            for (FIT_UINT8 i = 0; i < numElements; ++i) {
                FIT_UINT8* p = &fieldData[i * 8];
                std::swap(p[0], p[7]);
                std::swap(p[1], p[6]);
                std::swap(p[2], p[5]);
                std::swap(p[3], p[4]);
            }
            break;
        default:
            for (FIT_UINT8 element = 0; element < numElements; element++) {
                for (FIT_UINT8 i = 0; i < (typeSize / 2); i++) {
                    std::swap(fieldData[element * typeSize + i],
                              fieldData[element * typeSize + typeSize - i - 1]);
                }
            }
            break;
    }
}
