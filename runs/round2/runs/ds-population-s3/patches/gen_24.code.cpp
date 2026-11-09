FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const FIT_UINT8 t = GetType();
    if (t != FIT_BASE_TYPE_STRING)
    {
        static constexpr FIT_UINT8 shifts[32] = {
            0, 0, 0, 1, 1, 2, 2, 0, 2, 3, 0, 1, 2, 0, 3, 3, 3,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        };
        return (FIT_UINT8)(values.size() >> shifts[t & FIT_BASE_TYPE_NUM_MASK]);
    }

    return (FIT_UINT8)stringIndexes.size();
}
