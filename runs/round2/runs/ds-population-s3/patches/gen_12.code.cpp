FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    const FIT_UINT8 type = GetType();
    const FIT_UINT8 typeSize = baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE *>(data);

    if (type == FIT_BASE_TYPE_STRING)
    {
        FIT_UINT8 index = 0;
        while (index < size && byteData[index] == 0)
        {
            ++index;
        }

        if (index == size)
        {
            values.clear();
            return FIT_TRUE;
        }

        stringIndexes.push_back(0);

        values.assign(byteData, byteData + size);
        if (values.back() != 0)
        {
            values.push_back(0);
        }

        for (FIT_UINT8 i = 0; i + 2 < size; ++i)
        {
            if (byteData[i] == 0)
            {
                stringIndexes.push_back(static_cast<FIT_UINT8>(i + 1));
            }
        }
    }
    else
    {
        if (size == 0)
        {
            values.clear();
            return FIT_TRUE;
        }

        const FIT_BYTE *invalid = baseTypeInvalids[type & FIT_BASE_TYPE_NUM_MASK];
        const FIT_BYTE *point = byteData;
        int bytes = size;
        bool hasData = false;

        switch (typeSize)
        {
            case 1:
            {
                const FIT_BYTE invalidValue = invalid[0];
                while (bytes > 0)
                {
                    if (*point != invalidValue)
                    {
                        hasData = true;
                        break;
                    }
                    ++point;
                    --bytes;
                }
                break;
            }
            case 2:
            {
                std::uint16_t invalidValue;
                std::memcpy(&invalidValue, invalid, sizeof(invalidValue));
                while (bytes > 0)
                {
                    std::uint16_t value;
                    std::memcpy(&value, point, sizeof(value));
                    if (value != invalidValue)
                    {
                        hasData = true;
                        break;
                    }
                    point += 2;
                    bytes -= 2;
                }
                break;
            }
            case 4:
            {
                std::uint32_t invalidValue;
                std::memcpy(&invalidValue, invalid, sizeof(invalidValue));
                while (bytes > 0)
                {
                    std::uint32_t value;
                    std::memcpy(&value, point, sizeof(value));
                    if (value != invalidValue)
                    {
                        hasData = true;
                        break;
                    }
                    point += 4;
                    bytes -= 4;
                }
                break;
            }
            case 8:
            {
                std::uint64_t invalidValue;
                std::memcpy(&invalidValue, invalid, sizeof(invalidValue));
                while (bytes > 0)
                {
                    std::uint64_t value;
                    std::memcpy(&value, point, sizeof(value));
                    if (value != invalidValue)
                    {
                        hasData = true;
                        break;
                    }
                    point += 8;
                    bytes -= 8;
                }
                break;
            }
            default:
            {
                while (bytes > 0)
                {
                    if (std::memcmp(point, invalid, typeSize) != 0)
                    {
                        hasData = true;
                        break;
                    }
                    point += typeSize;
                    bytes -= typeSize;
                }
                break;
            }
        }

        if (hasData)
        {
            values.assign(byteData, byteData + size);
        }
        else
        {
            values.clear();
        }
    }

    return FIT_TRUE;
}
