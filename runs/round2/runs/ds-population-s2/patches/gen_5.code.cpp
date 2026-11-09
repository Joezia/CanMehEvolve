FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (num == FIT_UINT8_INVALID)
        return 0;

    if (type != FIT_BASE_TYPE_STRING)
    {
        static constexpr FIT_UINT8 shifts[17] =
            {0, 0, 0, 1, 1, 2, 2, 0, 2, 3, 0, 1, 2, 0, 3, 3, 3};
        return (FIT_UINT8)(values.size() >> shifts[type & FIT_BASE_TYPE_NUM_MASK]);
    }

    return (FIT_UINT8)stringIndexes.size();
}
