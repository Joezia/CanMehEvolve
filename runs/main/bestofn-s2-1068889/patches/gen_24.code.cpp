
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    T rv = 0;
    const FIT_UINT8 offset = fieldArrayIndex * size;
    std::memcpy(&rv, &values[offset], size);
    return rv;
}
