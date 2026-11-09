FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const auto fieldType = GetType();
    if (fieldType != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 baseTypeSize = baseTypeSizes[fieldType & FIT_BASE_TYPE_NUM_MASK];
        if (baseTypeSize == 0 || (baseTypeSize & (baseTypeSize - 1)) != 0)
            return (FIT_UINT8)(values.size() / baseTypeSize);
        return (FIT_UINT8)(values.size() >> __builtin_ctz(baseTypeSize));
    }

    return (FIT_UINT8)stringIndexes.size();
}
