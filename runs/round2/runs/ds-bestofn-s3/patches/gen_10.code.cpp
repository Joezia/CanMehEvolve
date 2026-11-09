FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (fieldId == FIT_FIELD_ID_INVALID)
        return 0;

    const FIT_UINT8 t = type;
    if (t != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 sz = baseTypeSizes[t & FIT_BASE_TYPE_NUM_MASK];
        switch (sz)
        {
            case 1: return static_cast<FIT_UINT8>(values.size());
            case 2: return static_cast<FIT_UINT8>(values.size() >> 1);
            case 4: return static_cast<FIT_UINT8>(values.size() >> 2);
            case 8: return static_cast<FIT_UINT8>(values.size() >> 3);
            default: return static_cast<FIT_UINT8>(values.size() / sz);
        }
    }

    return static_cast<FIT_UINT8>(stringIndexes.size());
}
