
FIT_UINT8 FieldBase::GetNumValues(void) const
{
    if (!IsValid())
        return 0;

    const auto type = GetType();
    if (type != FIT_BASE_TYPE_STRING) {
        const auto sizeIndex = type & FIT_BASE_TYPE_NUM_MASK;
        // Avoid division by using precomputed reciprocal or branch elimination
        // Since baseTypeSizes is likely small and constant, branch on sizeIndex
        // and use multiplication inverse if needed, but simplest fast path:
        return (FIT_UINT8)(values.size() / baseTypeSizes[sizeIndex]);
    }
    return (FIT_UINT8)stringIndexes.size();
}
