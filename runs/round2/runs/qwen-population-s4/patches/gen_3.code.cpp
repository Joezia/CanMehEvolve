
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    if (fieldArrayIndex >= (FIT_UINT8)values.size()) {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    const FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    const FIT_UINT8* ptr = &values[(fieldArrayIndex * size)];
    T rv = 0;
    std::memcpy(&rv, ptr, size);
    return rv;
}
