FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    const FIT_UINT8 type = GetType();
    const FIT_UINT8 typeIndex = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 typeSize = baseTypeSizes[typeIndex];
    FIT_BYTE *byteData = (FIT_BYTE *) data;

    values.clear();

    if (type == FIT_BASE_TYPE_STRING)
    {
        FIT_UINT8 index = 0;
        while (index < size)
        {
            if (byteData[index] != 0)
                break;
            ++index;
        }

        if (index == size)
            return FIT_TRUE;

        stringIndexes.push_back(0);

        values.reserve(size + 1);
        values.assign(byteData, byteData + size);

        if (size > 2)
        {
            const FIT_UINT8 limit = size - 2;
            for (FIT_UINT8 i = 0; i < limit; ++i)
            {
                if (byteData[i] == 0)
                    stringIndexes.push_back(i + 1);
            }
        }

        if (values.back() != 0)
            values.push_back(0);
    }
    else
    {
        const FIT_BYTE *invalid = baseTypeInvalids[typeIndex];

        if (typeSize == 1)
        {
            const FIT_BYTE invalidByte = invalid[0];
            const FIT_BYTE *point = byteData;
            int bytes = size;
            while (bytes > 0)
            {
                if (*point != invalidByte)
                {
                    values.assign(byteData, byteData + size);
                    break;
                }
                ++point;
                --bytes;
            }
        }
        else if (typeSize == 2)
        {
            FIT_UINT16 invalidValue;
            std::memcpy(&invalidValue, invalid, 2);
            const FIT_BYTE *point = byteData;
            int bytes = size;
            while (bytes > 0)
            {
                FIT_UINT16 value;
                std::memcpy(&value, point, 2);
                if (value != invalidValue)
                {
                    values.assign(byteData, byteData + size);
                    break;
                }
                point += 2;
                bytes -= 2;
            }
        }
        else if (typeSize == 4)
        {
            FIT_UINT32 invalidValue;
            std::memcpy(&invalidValue, invalid, 4);
            const FIT_BYTE *point = byteData;
            int bytes = size;
            while (bytes > 0)
            {
                FIT_UINT32 value;
                std::memcpy(&value, point, 4);
                if (value != invalidValue)
                {
                    values.assign(byteData, byteData + size);
                    break;
                }
                point += 4;
                bytes -= 4;
            }
        }
        else if (typeSize == 8)
        {
            FIT_UINT64 invalidValue;
            std::memcpy(&invalidValue, invalid, 8);
            const FIT_BYTE *point = byteData;
            int bytes = size;
            while (bytes > 0)
            {
                FIT_UINT64 value;
                std::memcpy(&value, point, 8);
                if (value != invalidValue)
                {
                    values.assign(byteData, byteData + size);
                    break;
                }
                point += 8;
                bytes -= 8;
            }
        }
        else
        {
            const FIT_BYTE *point = byteData;
            int bytes = size;
            while (bytes > 0)
            {
                if (std::memcmp(point, invalid, typeSize) != 0)
                {
                    values.assign(byteData, byteData + size);
                    break;
                }
                point += typeSize;
                bytes -= typeSize;
            }
        }
    }

    return FIT_TRUE;
}
