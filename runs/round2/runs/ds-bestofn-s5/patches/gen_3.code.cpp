FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (baseType == FIT_BASE_TYPE_INVALID)
        return 0;

    const FIT_UINT8 type = (FIT_UINT8)(baseType & FIT_BASE_TYPE_NUM_MASK);
    if (type != FIT_BASE_TYPE_STRING)
        return (FIT_UINT8)(values.size() >> __builtin_ctz(baseTypeSizes[type]));

    return (FIT_UINT8)stringIndexes.size();
}
