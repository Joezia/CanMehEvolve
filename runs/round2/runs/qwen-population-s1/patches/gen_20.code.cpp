
FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const FIT_UINT8 type = GetType();
    if (type != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 size = baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK];
        return (FIT_UINT8)(values.size() / size);
    }

    return (FIT_UINT8)stringIndexes.size();
}
