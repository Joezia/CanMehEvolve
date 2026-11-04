FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const auto type = GetType();
    if (type != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 idx = (FIT_UINT8)(type & FIT_BASE_TYPE_NUM_MASK);
        if (idx < 16)
        {
            static constexpr FIT_UINT8 shifts[16] = {0,0,1,1,2,2,0,2,3,0,1,2,0,3,3,3};
            return (FIT_UINT8)(values.size() >> shifts[idx]);
        }
        return (FIT_UINT8)(values.size() / baseTypeSizes[idx]);
    }

    return (FIT_UINT8)stringIndexes.size();
}
