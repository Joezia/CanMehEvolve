FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (num == FIT_UINT8_INVALID)
        return 0;

    const FIT_BASE_TYPE fieldType = GetType();
    if (fieldType != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 size = baseTypeSizes[fieldType & FIT_BASE_TYPE_NUM_MASK];
        if (size == 0 || (size & (size - 1)) != 0)
            return (FIT_UINT8)(values.size() / size);
        return (FIT_UINT8)(values.size() >> __builtin_ctz(size));
    }

    return (FIT_UINT8)stringIndexes.size();
}
