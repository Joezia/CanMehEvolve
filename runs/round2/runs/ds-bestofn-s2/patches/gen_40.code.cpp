FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (num == FIT_FIELD_NUM_INVALID)
        return 0;

    const FIT_UINT8 fieldType = type;
    if (fieldType != FIT_BASE_TYPE_STRING)
    {
        const auto numValues = values.size();
        const FIT_UINT8 baseTypeSize = baseTypeSizes[fieldType & FIT_BASE_TYPE_NUM_MASK];
        switch (baseTypeSize)
        {
            case 1: return (FIT_UINT8)numValues;
            case 2: return (FIT_UINT8)(numValues >> 1);
            case 4: return (FIT_UINT8)(numValues >> 2);
            case 8: return (FIT_UINT8)(numValues >> 3);
            default: return (FIT_UINT8)(numValues / baseTypeSize);
        }
    }

    return (FIT_UINT8)stringIndexes.size();
}
