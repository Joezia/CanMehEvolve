FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    const FIT_UINT8 type = GetType();
    FIT_BYTE *byteData = (FIT_BYTE *) data;

    values.clear();

    if (type == FIT_BASE_TYPE_STRING)
    {
        const FIT_BYTE* p = byteData;
        const FIT_BYTE* const end = byteData + size;
        while (p != end && *p == 0)
            ++p;
        if (p == end)
            return FIT_TRUE;

        stringIndexes.push_back(0);
        values.insert(values.end(), byteData, byteData + size);

        if (size > 2)
        {
            const FIT_UINT8 limit = size - 2;
            for (FIT_UINT8 i = 0; i < limit; ++i)
            {
                if (byteData[i] == 0)
                    stringIndexes.push_back((FIT_UINT8)(i + 1));
            }
        }

        if (values.back() != 0)
            values.push_back(0);

        return FIT_TRUE;
    }

    const FIT_UINT8 typeIndex = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_BYTE* invalid = baseTypeInvalids[typeIndex];
    const FIT_UINT8 typeSize = baseTypeSizes[typeIndex];

    const FIT_BYTE* point = byteData;
    int bytes = size;
    bool found = false;

    switch (typeSize)
    {
        case 1:
        {
            const FIT_BYTE inv = invalid[0];
            while (bytes > 0)
            {
                if (*point != inv)
                {
                    found = true;
                    break;
                }
                ++point;
                --bytes;
            }
            break;
        }
        case 2:
        {
            std::uint16_t inv;
            std::memcpy(&inv, invalid, 2);
            while (bytes >= 2)
            {
                std::uint16_t v;
                std::memcpy(&v, point, 2);
                if (v != inv)
                {
                    found = true;
                    break;
                }
                point += 2;
                bytes -= 2;
            }
            if (!found && bytes > 0 && std::memcmp(point, invalid, 2) != 0)
                found = true;
            break;
        }
        case 4:
        {
            std::uint32_t inv;
            std::memcpy(&inv, invalid, 4);
            while (bytes >= 4)
            {
                std::uint32_t v;
                std::memcpy(&v, point, 4);
                if (v != inv)
                {
                    found = true;
                    break;
                }
                point += 4;
                bytes -= 4;
            }
            if (!found && bytes > 0 && std::memcmp(point, invalid, 4) != 0)
                found = true;
            break;
        }
        case 8:
        {
            std::uint64_t inv;
            std::memcpy(&inv, invalid, 8);
            while (bytes >= 8)
            {
                std::uint64_t v;
                std::memcpy(&v, point, 8);
                if (v != inv)
                {
                    found = true;
                    break;
                }
                point += 8;
                bytes -= 8;
            }
            if (!found && bytes > 0 && std::memcmp(point, invalid, 8) != 0)
                found = true;
            break;
        }
        default:
        {
            while (bytes > 0)
            {
                if (std::memcmp(point, invalid, typeSize) != 0)
                {
                    found = true;
                    break;
                }
                point += typeSize;
                bytes -= typeSize;
            }
            break;
        }
    }

    if (found)
        values.insert(values.end(), byteData, byteData + size);

    return FIT_TRUE;
}
