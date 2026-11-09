FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const FIT_UINT8 fieldType = GetType();
    if (fieldType != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 size = baseTypeSizes[fieldType & FIT_BASE_TYPE_NUM_MASK];
        switch (size)
        {
        case 1:
            return (FIT_UINT8)values.size();
        case 2:
            return (FIT_UINT8)(values.size() >> 1);
        case 4:
            return (FIT_UINT8)(values.size() >> 2);
        case 8:
            return (FIT_UINT8)(values.size() >> 3);
        default:
            return (FIT_UINT8)(values.size() / size);
        }
    }

    return (FIT_UINT8)stringIndexes.size();
}
