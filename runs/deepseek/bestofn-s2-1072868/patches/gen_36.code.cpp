FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const FIT_UINT8 type = GetType();
    if (type != FIT_BASE_TYPE_STRING)
    {
        const FIT_UINT8 size = baseTypeSizes[type & FIT_BASE_TYPE_NUM_MASK];
        const auto n = values.size();
        switch (size)
        {
        case 1:  return (FIT_UINT8)n;
        case 2:  return (FIT_UINT8)(n >> 1);
        case 4:  return (FIT_UINT8)(n >> 2);
        case 8:  return (FIT_UINT8)(n >> 3);
        default: return (FIT_UINT8)(n / size);
        }
    }

    return (FIT_UINT8)stringIndexes.size();
}
