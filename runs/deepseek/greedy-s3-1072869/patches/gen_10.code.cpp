FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (num == FIT_UINT8_INVALID)
        return 0;

    if (type == FIT_BASE_TYPE_STRING)
        return (FIT_UINT8)stringIndexes.size();

    return (FIT_UINT8)(values.size() >> (baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK] >> 1));
}
