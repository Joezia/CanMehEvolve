FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (num == FIT_FIELD_NUM_INVALID)
        return 0;

    const FIT_UINT8 t = type;
    if (t == FIT_BASE_TYPE_STRING)
        return (FIT_UINT8)stringIndexes.size();

    const FIT_UINT8 sz = baseTypeSizes[t & FIT_BASE_TYPE_NUM_MASK];
    const auto n = values.size();

    if (sz == 1)
        return (FIT_UINT8)n;
    if (sz == 2)
        return (FIT_UINT8)(n >> 1);
    if (sz == 4)
        return (FIT_UINT8)(n >> 2);
    if (sz == 8)
        return (FIT_UINT8)(n >> 3);

    return (FIT_UINT8)(n / sz);
}
