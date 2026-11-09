void Decode::UpdateEndianness(FIT_UINT8 type, FIT_UINT8 size)
{
    if ((type & FIT_BASE_TYPE_ENDIAN_FLAG) == 0)
        return;
    if ((archs[localMesgIndex] & FIT_ARCH_ENDIAN_MASK) == FIT_ARCH_ENDIAN_LITTLE)
        return;

    const FIT_UINT8 typeSize = baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK];
    FIT_UINT8* const data = fieldData;

    if (typeSize == 2)
    {
        const int numElements = size >> 1;
        for (int element = 0; element < numElements; ++element)
        {
            FIT_UINT8* p = data + (element << 1);
            FIT_UINT8 tmp = p[0];
            p[0] = p[1];
            p[1] = tmp;
        }
    }
    else if (typeSize == 4)
    {
        const int numElements = size >> 2;
        for (int element = 0; element < numElements; ++element)
        {
            FIT_UINT8* p = data + (element << 2);
            FIT_UINT8 t0 = p[0], t1 = p[1];
            p[0] = p[3];
            p[1] = p[2];
            p[2] = t1;
            p[3] = t0;
        }
    }
    else if (typeSize == 8)
    {
        const int numElements = size >> 3;
        for (int element = 0; element < numElements; ++element)
        {
            FIT_UINT8* p = data + (element << 3);
            FIT_UINT8 t0 = p[0], t1 = p[1], t2 = p[2], t3 = p[3];
            p[0] = p[7];
            p[1] = p[6];
            p[2] = p[5];
            p[3] = p[4];
            p[4] = t3;
            p[5] = t2;
            p[6] = t1;
            p[7] = t0;
        }
    }
    else if (typeSize >= 2)
    {
        const int numElements = size / typeSize;
        for (int element = 0; element < numElements; ++element)
        {
            FIT_UINT8* p = data + element * typeSize;
            for (int i = 0; i < (typeSize / 2); ++i)
            {
                FIT_UINT8 tmp = p[i];
                p[i] = p[typeSize - i - 1];
                p[typeSize - i - 1] = tmp;
            }
        }
    }
}
