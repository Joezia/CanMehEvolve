FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 type = GetType();
    FIT_UINT8 typeSize = baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK];
    FIT_BYTE *byteData = (FIT_BYTE *) data;

    values.clear();

    if (type == FIT_BASE_TYPE_STRING)
    {
        FIT_UINT8 index = 0;
        while (index < size && byteData[index] == 0)
            ++index;

        if (index == size)
            return FIT_TRUE;

        stringIndexes.push_back(0);
        values.insert(values.end(), byteData, byteData + size);

        if (size > 2)
        {
            const FIT_UINT8 limit = (FIT_UINT8)(size - 2);
            for (FIT_UINT8 i = 0; i < limit; ++i)
            {
                if (byteData[i] == 0)
                    stringIndexes.push_back((FIT_UINT8)(i + 1));
            }
        }

        if (values.back() != 0)
            values.push_back(0);
    }
    else
    {
        int bytes = size;
        FIT_BYTE *point = byteData;
        const FIT_BYTE *invalid = baseTypeInvalids[type & FIT_BASE_TYPE_NUM_MASK];

        if (typeSize == 1)
        {
            const FIT_BYTE inv = invalid[0];
            while (bytes > 0)
            {
                if (*point != inv)
                {
                    values.insert(values.end(), byteData, byteData + size);
                    break;
                }
                ++point;
                --bytes;
            }
        }
        else if (typeSize == 2)
        {
            uint16_t inv;
            std::memcpy(&inv, invalid, 2);
            while (bytes > 0)
            {
                uint16_t v;
                std::memcpy(&v, point, 2);
                if (v != inv)
                {
                    values.insert(values.end(), byteData, byteData + size);
                    break;
                }
                point += 2;
                bytes -= 2;
            }
        }
        else if (typeSize == 4)
        {
            uint32_t inv;
            std::memcpy(&inv, invalid, 4);
            while (bytes > 0)
            {
                uint32_t v;
                std::memcpy(&v, point, 4);
                if (v != inv)
                {
                    values.insert(values.end(), byteData, byteData + size);
                    break;
                }
                point += 4;
                bytes -= 4;
            }
        }
        else if (typeSize == 8)
        {
            uint64_t inv;
            std::memcpy(&inv, invalid, 8);
            while (bytes > 0)
            {
                uint64_t v;
                std::memcpy(&v, point, 8);
                if (v != inv)
                {
                    values.insert(values.end(), byteData, byteData + size);
                    break;
                }
                point += 8;
                bytes -= 8;
            }
        }
        else
        {
            while (bytes > 0)
            {
                if (std::memcmp(point, invalid, typeSize) != 0)
                {
                    values.insert(values.end(), byteData, byteData + size);
                    break;
                }
                point += typeSize;
                bytes -= typeSize;
            }
        }
    }

    return FIT_TRUE;
}
