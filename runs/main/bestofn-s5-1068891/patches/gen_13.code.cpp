
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        T invalid = 0;
        std::memcpy(&invalid, baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK], sizeof(T));
        return invalid;
    }

    T rv = 0;
    const FIT_UINT8* data = &values[(fieldArrayIndex * size)];
    std::memcpy(&rv, data, size);
    return rv;
}
